package A1;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Producer {
    public static void main(String[] argv) throws Exception {

        // info
        System.out.println("Z1 PRODUCER");

        // connection & channel
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // queue
        String QUEUE_NAME = "queue1";
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);

        // 1A

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String message;

        System.out.println("Enter your messages. Type 'exit' to quit.");

        while (true) {
            System.out.print("Enter message: ");
            message = br.readLine();

            if ("exit".equalsIgnoreCase(message)) {
                break;
            }

            channel.basicPublish("", QUEUE_NAME, null, message.getBytes());
            System.out.println("Sent: " + message);
        }


        // close
        channel.close();
        connection.close();
    }
}
