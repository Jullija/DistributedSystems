package A1;

import com.rabbitmq.client.*;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Consumer {
    public static void main(String[] argv) throws Exception {

        // info
        System.out.println("Z1 CONSUMER");

        // connection & channel
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // queue
        String QUEUE_NAME = "queue1";
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);

        // consumer (handle msg)
        DefaultConsumer consumer = new DefaultConsumer(channel) {
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
                String message = new String(body, "UTF-8");
                System.out.println("Received: " + message);

                try {
                    int timeToSleep = Integer.parseInt(message);
                    System.out.println("Sleeping for " + timeToSleep + " seconds...");
                    Thread.sleep(timeToSleep * 1000);
                    System.out.println("Done sleeping.");

                    //comment when using channel.basicConsume(QUEUE_NAME, true)
                    channel.basicAck(envelope.getDeliveryTag(), false);
                } catch (NumberFormatException e) {
                    System.err.println("Invalid sleep time received: " + message);
                } catch (InterruptedException e) {
                    System.err.println("Sleep interrupted.");
                }
            }
        };

        // start listening
        System.out.println("Waiting for messages...");
        //true - automatic ack
        channel.basicConsume(QUEUE_NAME, false, consumer);

        // close
//        channel.close();
//        connection.close();
    }
}
