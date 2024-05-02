from concurrent import futures
from random import choice, random

import grpc
import time

from proto import event_pb2, event_pb2_grpc


class EventServer(event_pb2_grpc.EventServiceServicer):
    def __init__(self):
        self.clients = {} #{client_id: client_name}
        self.next_client_id = 1
        self.events = [] #every event
        self.client_subscriptions = {} #{client_id: [event1, event2]}

    def addEvent(self, event_to_add):
        self.events.append(event_to_add)

    def GetClientSubscriptions(self, request, context):
        clients_events = self.client_subscriptions.get(request.client_id, [])
        return event_pb2.ClientSubscriptionsResponse(client_id = request.client_id, subscribed_events=clients_events)

    def ClientConnects(self, request, context):
        client_id = self.next_client_id
        print(f"Welcome aboard {request.client_name}! Your client id is {client_id}")

        self.next_client_id += 1
        self.clients[client_id] = request.client_name
        self.client_subscriptions[client_id] = []

        return event_pb2.ClientConnectsResponse(client_id=client_id, events=self.events)


    def ClientSubscribeLocation(self, request, context):
        client_id = request.client_id
        event_location = request.location
        subscribed_events = []
        subscribed = False
        for event in self.events:
            if event_location == event.location and client_id not in event.attendees_ids and event.max_attendees >= len(event.attendees_ids) + 1:
                subscribed = True
                subscribed_events.append(event)
                event.attendees_ids.append(client_id)
                self.client_subscriptions[client_id].append(event)



        if subscribed:
            return event_pb2.ClientSubscribeLocationResponse(client_id=client_id, events_list=subscribed_events, text=f"Subscribed for {subscribed_events}")
        else:
            return event_pb2.ClientSubscribeLocationResponse(client_id=client_id, events_list=[], text="Didn't subscribe for any events")

    def ClientSubscribeType(self, request, context):
        client_id = request.client_id
        event_type = request.type
        subscribed_events = []
        subscribed = False
        for event in self.events:
            if (event_type == event.type and client_id not in event.attendees_ids and event.max_attendees >= len(event.attendees_ids) + 1):
                subscribed = True
                subscribed_events.append(event)
                event.attendees_ids.append(client_id)
                self.client_subscriptions[client_id].append(event)



        if subscribed:
            return event_pb2.ClientSubscribeTypeResponse(client_id=client_id, events_list=subscribed_events, text=f"Subscribed for {subscribed_events}")
        else:
            return event_pb2.ClientSubscribeTypeResponse(client_id=client_id, events_list=[], text="Didn't subscribe for any events")



def create_events(num_events, server):
    event_type_values = [etype for etype in event_pb2.EventType.values() if etype != 0]
    location_type_values = [loc for loc in event_pb2.Location.values() if loc != 0]

    for i in range(num_events):
        event_type_random = choice(event_type_values)
        location_type_random = choice(location_type_values)

        event = event_pb2.Event(
            event_id=i+1,
            type=event_type_random,
            description="This is a random description",
            max_attendees=int(random() * 100 + 1),
            attendees_ids = [],
            location=location_type_random
        )

        server.addEvent(event)


def serve():
    event_server = EventServer()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    event_pb2_grpc.add_EventServiceServicer_to_server(event_server, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started at port 50051")
    create_events(5, event_server)
    print(event_server.events)

    server.wait_for_termination()



if __name__ == '__main__':
    serve()


