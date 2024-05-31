import pika
import threading
import sys

class Doctor:
    def __init__(self, doctor_id):
        self.doctor_id = doctor_id

        # Connection and channel for listening
        self.listen_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',heartbeat=600))
        self.listen_channel = self.listen_connection.channel()
        self.listen_channel.exchange_declare(exchange='hospital', exchange_type='topic')

        result = self.listen_channel.queue_declare(queue='', exclusive=True)
        self.result_queue = result.method.queue
        self.listen_channel.queue_bind(exchange='hospital', queue=self.result_queue, routing_key=f'result.{doctor_id}')

        self.listen_channel.queue_declare(queue=f'admin_info_queue_{doctor_id}')
        self.listen_channel.queue_bind(exchange='hospital', queue=f'admin_info_queue_{doctor_id}', routing_key='admin.info')

        self.listen_channel.basic_consume(queue=self.result_queue, on_message_callback=self.receive_results, auto_ack=True)
        self.listen_channel.basic_consume(queue=f'admin_info_queue_{doctor_id}', on_message_callback=self.receive_info, auto_ack=True)

        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

        # Connection and channel for sending
        self.send_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',heartbeat=600))
        self.send_channel = self.send_connection.channel()
        self.send_channel.exchange_declare(exchange='hospital', exchange_type='topic')

    def send_order(self, patient_name, exam_type):
        message = f"order:{self.doctor_id}:{patient_name}:{exam_type}"
        routing_key = f'order.{exam_type}'
        self.send_channel.basic_publish(exchange='hospital', routing_key=routing_key, body=message)
        # self.send_channel.basic_publish(exchange='hospital', routing_key='admin.log', body=message)
        print(f"[DOCTOR] Sent order: {message}")

    def receive_results(self, ch, method, properties, body):
        print(f"[DOCTOR] Received results: {body.decode()}")

    def receive_info(self, ch, method, properties, body):
        print(f"[DOCTOR] Received info: {body.decode()}")

    def listen(self):
        print(f"Doctor {self.doctor_id} started listening for results and admin info.")
        self.listen_channel.start_consuming()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python doctor.py <doctor_name>")
        sys.exit(1)
    doctor_name = sys.argv[1]
    doctor = Doctor(doctor_name)
    while True:
        patient_name = input("Enter patient name: ")
        exam_type = input("Enter exam type (hip, knee, elbow): ")
        doctor.send_order(patient_name, exam_type)
