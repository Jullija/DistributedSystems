package homework;

import java.io.*;
import java.net.*;

public class ChatClient {
    private static final String SERVER_ADDRESS = "127.0.0.1";
    private static final int SERVER_PORT = 12346;
    private static final String ASCII_MESSAGE =
            "     |\\_/|                  \n" +
                    "     | @ @   Woof! \n" +
                    "     |   <>              _  \n" +
                    "     |  _/\\------____ ((| |))\n" +
                    "     |               `--' |   \n" +
                    " ____|_       ___|   |___.' \n" +
                    "/_/_____/____/_______|";
    private static DatagramSocket udpSocket;
    private static volatile boolean running = true;



    private static void startUdpListener() {
        new Thread(() -> {
            byte[] buf = new byte[1024];
            while (running) {
                try {
                    DatagramPacket packet = new DatagramPacket(buf, buf.length);
                    udpSocket.receive(packet);
                    if (!running) break;
                    String received = new String(packet.getData(), 0, packet.getLength());
                    System.out.println(received);
                } catch (IOException e) {
                    if (!running) {
                        System.out.println("UDP Listener stopped.");
                    } else {
                        System.out.println("UDP Listener IOException: " + e.getMessage());
                    }
                }
            }
        }).start();
    }

    private static void sendUdpMessage(String message) throws IOException {
        byte[] buf = message.getBytes();
        InetAddress address = InetAddress.getByName(SERVER_ADDRESS);
        DatagramPacket packet = new DatagramPacket(buf, buf.length, address, SERVER_PORT);
        udpSocket.send(packet);
    }

    private static void sendEmptyUdpMessageToRegister() throws IOException {
        sendUdpMessage("");
    }

    public static void main(String[] args) throws Exception {
        try (Socket socket = new Socket(SERVER_ADDRESS, SERVER_PORT);
             BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
             BufferedReader inputReader = new BufferedReader(new InputStreamReader(System.in))) {
            String nickname;
            udpSocket = new DatagramSocket();
            startUdpListener();
            sendEmptyUdpMessageToRegister();

            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                try {
                    running = false;
                    out.println("quit");
                    udpSocket.close();
                    socket.close();
                    System.out.println("\nClient closed successfully.");
                } catch (IOException e) {
                    System.out.println("Error closing the client: " + e.getMessage());
                }
            }));

        while (true) {
            System.out.print("Enter your nickname: ");
            nickname = inputReader.readLine();
            out.println(nickname);
            String serverResponse = in.readLine();
            if ("NICKACCEPTED".equals(serverResponse)) {
                System.out.println("Nickname accepted!");
                break;
            } else {
                System.out.println("Nickname already in use or invalid, please try another.");
            }
        }

        Thread listenerThread = new Thread(() -> {
            try {
                String line;
                while ((line = in.readLine()) != null) {
                    System.out.println(line);
                }
            } catch (IOException e) {
                System.out.println(e);
            }
        });
        listenerThread.start();

        while (true) {
            String userInput = inputReader.readLine();
            if ("quit".equalsIgnoreCase(userInput.trim())) {
                out.println("quit");
                System.out.println("Quitting...");
                if (!socket.isClosed()) socket.close();
                if (!udpSocket.isClosed()) udpSocket.close();
                running = false;
                break;
            }else if (userInput.startsWith("u_ascii")){
                sendUdpMessage(ASCII_MESSAGE);
            }else if (userInput.startsWith("u")) {
                String messageWithNick = "UDP MESSAGE FROM " + nickname + ": " + userInput.substring(1);
                sendUdpMessage(messageWithNick);
            } else if (userInput != null) {
                out.println(userInput);
            }
        }
    } catch (Exception e) {
            System.out.println("damn, exception");
        }
    }
}
