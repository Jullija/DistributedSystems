from concurrent import futures
from random import choice, random
from queue import Queue, Empty
import threading
import pickle
import os
import grpc
import time

from proto import event_pb2, event_pb2_grpc


class EventServer(event_pb2_grpc.EventServiceServicer):
    def __init__(self):
        self.clients = {}  #{client_id: client_name}
        self.next_client_id = 1
        self.events = []  #every event
        self.client_subscriptions = {}  #{client_id: [event1, event2]}
        self.events_lock = threading.Lock()
        self.client_notification_channels = {} #{client_id: Queue()}

    def SubscribeToNotifications(self, request, context):
        client_id = request.client_id
        if client_id not in self.client_notification_channels:
            self.client_notification_channels[client_id] = Queue()

        queue = self.client_notification_channels[client_id]
        try:
            while context.is_active():
                try:
                    message = queue.get(timeout=10)
                    yield event_pb2.NotificationResponse(message=message)
                except Empty:
                    continue
        except Exception as e:
            print(f"Error while sending notifications to client {client_id}: {str(e)}")

    def addEvent(self, event_to_add):
        with self.events_lock:
            self.events.append(event_to_add)

    def GetClientSubscriptions(self, request, context):
        if request.client_id not in self.clients:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Client ID not found')
            return event_pb2.ClientSubscriptionsResponse()
        with self.events_lock:
            clients_events = self.client_subscriptions.get(request.client_id, [])
            return event_pb2.ClientSubscriptionsResponse(client_id=request.client_id, subscribed_events=clients_events)

    def ClientConnects(self, request, context):
        with self.events_lock:
            client_name = request.client_name.strip()
            if client_name in self.clients.values():
                client_id = list(self.clients.values()).index(client_name) + 1
                print(f"Welcome back {client_name}! Your client id is {client_id}")
            else:
                client_id = self.next_client_id
                print(f"Welcome aboard {client_name}! Your client id is {client_id}")

                self.next_client_id += 1
                self.clients[client_id] = client_name
                self.client_subscriptions[client_id] = []
                self.client_notification_channels[client_id] = Queue()

            return event_pb2.ClientConnectsResponse(client_id=client_id, events=self.events)

    def ClientSubscribeLocation(self, request, context):
        with self.events_lock:
            client_id = request.client_id
            event_location = request.location
            subscribed_events = []
            subscribed = False
            for event in self.events:
                if event_location == event.location and client_id not in event.attendees_ids and event.max_attendees >= len(
                        event.attendees_ids) + 1:
                    subscribed = True
                    subscribed_events.append(event)
                    event.attendees_ids.append(client_id)
                    self.client_subscriptions[client_id].append(event)

            if subscribed:
                return event_pb2.ClientSubscribeLocationResponse(client_id=client_id, events_list=subscribed_events,
                                                                 text=f"Subscribed for {subscribed_events}")
            else:
                return event_pb2.ClientSubscribeLocationResponse(client_id=client_id, events_list=[],
                                                                 text="Didn't subscribe for any events")

    def ClientSubscribeType(self, request, context):
        with self.events_lock:
            client_id = request.client_id
            event_type = request.type
            subscribed_events = []
            subscribed = False
            for event in self.events:
                if (event_type == event.type and client_id not in event.attendees_ids and event.max_attendees >= len(
                        event.attendees_ids) + 1):
                    subscribed = True
                    subscribed_events.append(event)
                    event.attendees_ids.append(client_id)
                    self.client_subscriptions[client_id].append(event)

            if subscribed:
                return event_pb2.ClientSubscribeTypeResponse(client_id=client_id, events_list=subscribed_events,
                                                             text=f"Subscribed for {subscribed_events}")
            else:
                return event_pb2.ClientSubscribeTypeResponse(client_id=client_id, events_list=[],
                                                             text="Didn't subscribe for any events")


def update_events(server):
    event_type_values = [etype for etype in event_pb2.EventType.values() if etype != 0]
    location_type_values = [loc for loc in event_pb2.Location.values() if loc != 0]

    while True:
        time.sleep(10)
        with server.events_lock:
            if server.events:
                event = choice(server.events)
                old_location = event.location
                old_type = event.type
                event.type = choice(event_type_values)
                event.location = choice(location_type_values)
                if old_location != event.location or old_type != event.type:
                    notify_subscribed_clients(server, event)
                print(event)


def notify_subscribed_clients(server, event):
    event_type_name = event_pb2.EventType.Name(event.type)
    event_location_name = event_pb2.Location.Name(event.location)
    message = f"Event {event.event_id} has been updated. New Type: {event_type_name}, New Location: {event_location_name}"
    for client_id in event.attendees_ids:
        if client_id in server.client_notification_channels:
            server.client_notification_channels[client_id].put_nowait(message)


def save_server_state(server):
    try:
        with open('server_state.pkl', 'wb') as f:
            pickle.dump({
                'clients': server.clients,
                'next_client_id': server.next_client_id,
                'events': server.events,
                'client_subscriptions': server.client_subscriptions
            }, f)
        print("Server state saved successfully.")
    except Exception as e:
        print("Error saving server state:", e)

def load_server_state(server):
    state_file = 'server_state.pkl'
    if os.path.exists(state_file):
        try:
            file_time = os.path.getmtime(state_file)
            if (time.time() - file_time) <= 10:  # Check if the file was saved less than 10 seconds ago
                with open(state_file, 'rb') as f:
                    state = pickle.load(f)
                    server.clients = state['clients']
                    server.next_client_id = state['next_client_id']
                    server.events = state['events']
                    server.client_subscriptions = state['client_subscriptions']
                    print("Server state loaded successfully.")
            else:
                print("Saved state is too old, starting fresh.")
        except Exception as e:
            print("Error loading server state:", e)
    else:
        print("No saved state found, starting fresh.")

def create_events(num_events, server):
    event_type_values = [etype for etype in event_pb2.EventType.values() if etype != 0]
    location_type_values = [loc for loc in event_pb2.Location.values() if loc != 0]

    for i in range(num_events):
        event_type_random = choice(event_type_values)
        location_type_random = choice(location_type_values)

        event = event_pb2.Event(
            event_id=i + 1,
            type=event_type_random,
            description="This is a random description",
            max_attendees=int(random() * 100 + 1),
            attendees_ids=[],
            location=location_type_random
        )

        server.addEvent(event)


def serve():
    from concurrent import futures
    from random import choice, random
    from queue import Queue, Empty
    import threading
    import pickle
    import os
    import grpc
    import time

    from proto import event_pb2, event_pb2_grpc

    class EventServer(event_pb2_grpc.EventServiceServicer):
        def __init__(self):
            self.clients = {}  # {client_id: client_name}
            self.next_client_id = 1
            self.events = []  # every event
            self.client_subscriptions = {}  # {client_id: [event1, event2]}
            self.events_lock = threading.Lock()
            self.client_notification_channels = {}  # {client_id: Queue()}

        def SubscribeToNotifications(self, request, context):
            client_id = request.client_id
            if client_id not in self.client_notification_channels:
                self.client_notification_channels[client_id] = Queue()

            queue = self.client_notification_channels[client_id]
            try:
                while context.is_active():
                    try:
                        message = queue.get(timeout=10)
                        yield event_pb2.NotificationResponse(message=message)
                    except Empty:
                        continue
            except Exception as e:
                print(f"Error while sending notifications to client {client_id}: {str(e)}")

        def addEvent(self, event_to_add):
            with self.events_lock:
                self.events.append(event_to_add)

        def GetClientSubscriptions(self, request, context):
            if request.client_id not in self.clients:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('Client ID not found')
                return event_pb2.ClientSubscriptionsResponse()
            with self.events_lock:
                clients_events = self.client_subscriptions.get(request.client_id, [])
                return event_pb2.ClientSubscriptionsResponse(client_id=request.client_id,
                                                             subscribed_events=clients_events)

        def ClientConnects(self, request, context):
            with self.events_lock:
                client_name = request.client_name.strip()
                if client_name in self.clients.values():
                    client_id = list(self.clients.values()).index(client_name) + 1
                    print(f"Welcome back {client_name}! Your client id is {client_id}")
                else:
                    client_id = self.next_client_id
                    print(f"Welcome aboard {client_name}! Your client id is {client_id}")

                    self.next_client_id += 1
                    self.clients[client_id] = client_name
                    self.client_subscriptions[client_id] = []
                    self.client_notification_channels[client_id] = Queue()

                return event_pb2.ClientConnectsResponse(client_id=client_id, events=self.events)

        def ClientSubscribeLocation(self, request, context):
            with self.events_lock:
                client_id = request.client_id
                event_location = request.location
                subscribed_events = []
                subscribed = False
                for event in self.events:
                    if event_location == event.location and client_id not in event.attendees_ids and event.max_attendees >= len(
                            event.attendees_ids) + 1:
                        subscribed = True
                        subscribed_events.append(event)
                        event.attendees_ids.append(client_id)
                        self.client_subscriptions[client_id].append(event)

                if subscribed:
                    return event_pb2.ClientSubscribeLocationResponse(client_id=client_id, events_list=subscribed_events,
                                                                     text=f"Subscribed for {subscribed_events}")
                else:
                    return event_pb2.ClientSubscribeLocationResponse(client_id=client_id, events_list=[],
                                                                     text="Didn't subscribe for any events")

        def ClientSubscribeType(self, request, context):
            with self.events_lock:
                client_id = request.client_id
                event_type = request.type
                subscribed_events = []
                subscribed = False
                for event in self.events:
                    if (
                            event_type == event.type and client_id not in event.attendees_ids and event.max_attendees >= len(
                            event.attendees_ids) + 1):
                        subscribed = True
                        subscribed_events.append(event)
                        event.attendees_ids.append(client_id)
                        self.client_subscriptions[client_id].append(event)

                if subscribed:
                    return event_pb2.ClientSubscribeTypeResponse(client_id=client_id, events_list=subscribed_events,
                                                                 text=f"Subscribed for {subscribed_events}")
                else:
                    return event_pb2.ClientSubscribeTypeResponse(client_id=client_id, events_list=[],
                                                                 text="Didn't subscribe for any events")

    def update_events(server):
        event_type_values = [etype for etype in event_pb2.EventType.values() if etype != 0]
        location_type_values = [loc for loc in event_pb2.Location.values() if loc != 0]

        while True:
            time.sleep(10)
            with server.events_lock:
                if server.events:
                    event = choice(server.events)
                    old_location = event.location
                    old_type = event.type
                    event.type = choice(event_type_values)
                    event.location = choice(location_type_values)
                    if old_location != event.location or old_type != event.type:
                        notify_subscribed_clients(server, event)
                    print(event)

    def notify_subscribed_clients(server, event):
        event_type_name = event_pb2.EventType.Name(event.type)
        event_location_name = event_pb2.Location.Name(event.location)
        message = f"Event {event.event_id} has been updated. New Type: {event_type_name}, New Location: {event_location_name}"
        for client_id in event.attendees_ids:
            if client_id in server.client_notification_channels:
                server.client_notification_channels[client_id].put_nowait(message)

    def save_server_state(server):
        try:
            with open('server_state.pkl', 'wb') as f:
                pickle.dump({
                    'clients': server.clients,
                    'next_client_id': server.next_client_id,
                    'events': server.events,
                    'client_subscriptions': server.client_subscriptions
                }, f)
            print("Server state saved successfully.")
        except Exception as e:
            print("Error saving server state:", e)

    def load_server_state(server):
        state_file = 'server_state.pkl'
        if os.path.exists(state_file):
            try:
                file_time = os.path.getmtime(state_file)
                if (time.time() - file_time) <= 10:  # Check if the file was saved less than 10 seconds ago
                    with open(state_file, 'rb') as f:
                        state = pickle.load(f)
                        server.clients = state['clients']
                        server.next_client_id = state['next_client_id']
                        server.events = state['events']
                        server.client_subscriptions = state['client_subscriptions']
                        print("Server state loaded successfully.")
                else:
                    print("Saved state is too old, starting fresh.")
            except Exception as e:
                print("Error loading server state:", e)
        else:
            print("No saved state found, starting fresh.")

    def create_events(num_events, server):
        event_type_values = [etype for etype in event_pb2.EventType.values() if etype != 0]
        location_type_values = [loc for loc in event_pb2.Location.values() if loc != 0]

        for i in range(num_events):
            event_type_random = choice(event_type_values)
            location_type_random = choice(location_type_values)

            event = event_pb2.Event(
                event_id=i + 1,
                type=event_type_random,
                description="This is a random description",
                max_attendees=int(random() * 100 + 1),
                attendees_ids=[],
                location=location_type_random
            )

            server.addEvent(event)

    def serve():
        server_options = [
            ('grpc.keepalive_time_ms', 60000),  # Interval for keepalive ping (60 seconds)
            ('grpc.keepalive_timeout_ms', 30000),  # Timeout for ping response (30 seconds)
            ('grpc.keepalive_permit_without_calls', 1),  # Allow pings even when there are no calls
            ('grpc.http2.min_time_between_pings_ms', 1000),  # Minimum time between pings
            ('grpc.http2.min_ping_interval_without_data_ms', 1000),  # Minimum time between pings when no data
            ('grpc.http2.max_pings_without_data', 0),  # Unlimited pings without data
        ]

        event_server = EventServer()
        load_server_state(event_server)
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=server_options)
        event_pb2_grpc.add_EventServiceServicer_to_server(event_server, server)
        server.add_insecure_port('[::]:50051')
        server.start()
        create_events(5, event_server) if not event_server.events else None
        update_thread = threading.Thread(target=update_events, args=(event_server,), daemon=True)
        update_thread.start()
        print("Server started at port 50051")
        print(event_server.events)

        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            save_server_state(event_server)
            server.stop(0)
            update_thread.join()

    if __name__ == '__main__':
        serve()

    event_server = EventServer()
    load_server_state(event_server)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    event_pb2_grpc.add_EventServiceServicer_to_server(event_server, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    create_events(5, event_server) if not event_server.events else None
    update_thread = threading.Thread(target=update_events, args=(event_server,), daemon=True)
    update_thread.start()
    print("Server started at port 50051")
    print(event_server.events)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        save_server_state(event_server)
        server.stop(0)
        update_thread.join()



if __name__ == '__main__':
    serve()
