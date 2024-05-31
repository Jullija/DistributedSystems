import pika
import threading
import sys

class Technician:
    def __init__(self, tech_id, exam_types):
        self.tech_id = tech_id
        self.exam_types = exam_types.split(',')
        print(exam_types)

        # Connection and channel for listening
        self.listen_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',heartbeat=600))
        self.listen_channel = self.listen_connection.channel()
        self.listen_channel.exchange_declare(exchange='hospital', exchange_type='topic')

        for exam_type in self.exam_types:
            queue_name = f'{exam_type}_queue'
            self.listen_channel.queue_declare(queue=queue_name)
            self.listen_channel.queue_bind(exchange='hospital', queue=queue_name, routing_key=f'order.{exam_type}') #queue for every exam type

        self.listen_channel.queue_declare(queue=f'admin_info_queue_{tech_id}') 
        self.listen_channel.queue_bind(exchange='hospital', queue=f'admin_info_queue_{tech_id}', routing_key='admin.info') #queue for every tech_id

        for exam_type in self.exam_types:
            queue_name = f'{exam_type}_queue'
            self.listen_channel.basic_consume(queue=queue_name, on_message_callback=self.process_order, auto_ack=True)
        self.listen_channel.basic_consume(queue=f'admin_info_queue_{tech_id}', on_message_callback=self.receive_info, auto_ack=True)

        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

        # Connection and channel for sending
        self.send_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',heartbeat=600))
        self.send_channel = self.send_connection.channel()
        self.send_channel.exchange_declare(exchange='hospital', exchange_type='topic')

    def process_order(self, ch, method, properties, body):
        message = body.decode()
        _, doctor_id, patient_name, exam_type = message.split(":")
        if exam_type in self.exam_types:
            result = f"{patient_name}:{exam_type}:done"
            routing_key = f'result.{doctor_id}'
            self.send_channel.basic_publish(exchange='hospital', routing_key=routing_key, body=result)
            log_message = f"{self.tech_id} processed order: {message} -> {result}"
            #self.send_channel.basic_publish(exchange='hospital', routing_key='admin.log', body=log_message)
            print(f"[TECH] Processed order: {message} -> {result}")

    def receive_info(self, ch, method, properties, body):
        print(f"[TECH] Received info: {body.decode()}")

    def listen(self):
        print(f"Technician {self.tech_id} started listening for orders and admin info.")
        self.listen_channel.start_consuming()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python technician.py <tech_name> <exam_types>")
        sys.exit(1)
    tech_name = sys.argv[1]
    exam_types = sys.argv[2]
    technician = Technician(tech_name, exam_types)
