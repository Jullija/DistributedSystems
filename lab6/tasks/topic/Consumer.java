package topic;

import com.rabbitmq.client.*;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Consumer {
    public static void main(String[] argv) throws Exception {

        // info
        System.out.println("Topic Exchange Consumer");

        // connection & channel
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // exchange
        String EXCHANGE_NAME = "topic_exchange";
        channel.exchangeDeclare(EXCHANGE_NAME, BuiltinExchangeType.TOPIC);

        // read routing key pattern
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("Enter routing key pattern: ");
        String routingKeyPattern = br.readLine();

        // queue & bind
        String queueName = channel.queueDeclare().getQueue();
        channel.queueBind(queueName, EXCHANGE_NAME, routingKeyPattern);
        System.out.println("Created queue: " + queueName + " with routing key pattern: " + routingKeyPattern);

        // consumer (message handling)
        com.rabbitmq.client.Consumer consumer = new DefaultConsumer(channel) {
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
                String message = new String(body, "UTF-8");
                System.out.println("Received: '" + message + "' with routing key: '" + envelope.getRoutingKey() + "'");
            }
        };

        // start listening
        System.out.println("Waiting for messages...");
        channel.basicConsume(queueName, true, consumer);
    }
}
