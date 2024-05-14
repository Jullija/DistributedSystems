package topic;

import com.rabbitmq.client.BuiltinExchangeType;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Producer {
    public static void main(String[] argv) throws Exception {

        // info
        System.out.println("Topic Exchange Producer");

        // connection & channel
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // exchange
        String EXCHANGE_NAME = "topic_exchange";
        channel.exchangeDeclare(EXCHANGE_NAME, BuiltinExchangeType.TOPIC);

        while (true) {
            // read routing key and message
            BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
            System.out.println("Enter routing key: ");
            String routingKey = br.readLine();
            System.out.println("Enter message: ");
            String message = br.readLine();

            // break condition
            if ("exit".equals(message)) {
                break;
            }

            // publish
            channel.basicPublish(EXCHANGE_NAME, routingKey, null, message.getBytes("UTF-8"));
            System.out.println("Sent: '" + message + "' with routing key: '" + routingKey + "'");
        }

        channel.close();
        connection.close();
    }
}
