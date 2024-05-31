import pika
import threading

class Administrator:
    def __init__(self):
        # Connection and channel for listening
        self.listen_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=600))
        self.listen_channel = self.listen_connection.channel()
        self.listen_channel.exchange_declare(exchange='hospital', exchange_type='topic')

        self.listen_channel.queue_declare(queue='admin_queue')
        self.listen_channel.queue_bind(exchange='hospital', queue='admin_queue', routing_key='#')

        self.listen_channel.basic_consume(queue='admin_queue', on_message_callback=self.log_activity, auto_ack=True)

        # Connection and channel for sending
        self.send_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=600))
        self.send_channel = self.send_connection.channel()
        self.send_channel.exchange_declare(exchange='hospital', exchange_type='topic')

    def log_activity(self, ch, method, properties, body):
        print(f"[ADMIN] Log: {body.decode()}")

    def listen(self):
        print("Administrator started listening for logs.")
        self.listen_channel.start_consuming()

    def send_info(self, message):
        routing_key = "admin.info"
        self.send_channel.basic_publish(exchange='hospital', routing_key=routing_key, body=message)
        print(f"[ADMIN] Sent info: {message}")

if __name__ == "__main__":
    admin = Administrator()
    listen_thread = threading.Thread(target=admin.listen)
    listen_thread.start()

    while True:
        info_message = input("Enter info message to send to all: ")
        admin.send_info(info_message)
