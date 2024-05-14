package direct;

import com.rabbitmq.client.*;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Consumer {
    public static void main(String[] argv) throws Exception {

        // info
        System.out.println("Direct Exchange Consumer");

        // connection & channel
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // exchange
        String EXCHANGE_NAME = "direct";
        channel.exchangeDeclare(EXCHANGE_NAME, BuiltinExchangeType.DIRECT);

        // read routing key
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        System.out.println("Enter routing key: ");
        String routingKey = br.readLine();

        // queue & bind
        String queueName = channel.queueDeclare().getQueue();
        channel.queueBind(queueName, EXCHANGE_NAME, routingKey);
        System.out.println("Created queue: " + queueName + " with routing key: " + routingKey);

        // consumer (message handling)
        DefaultConsumer consumer = new DefaultConsumer(channel) {
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
