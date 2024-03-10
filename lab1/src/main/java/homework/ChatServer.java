package homework;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class ChatServer {
    private static final int PORT = 12346;
    private static Map<String, PrintWriter> clients = new HashMap<>();
    private static final Set<InetSocketAddress> clientAddresses = ConcurrentHashMap.newKeySet();


    public static void main(String[] args) throws Exception {
        System.out.println("Server running...");
        ServerSocket listener = new ServerSocket(PORT);
        startUdpThread();


        try {
            while (true) {
                new Handler(listener.accept()).start();
            }
        } finally {
            listener.close();
        }
    }

    private static class Handler extends Thread {
        private String nick;
        private Socket socket;
        private BufferedReader in;
        private PrintWriter out;

        public Handler(Socket socket) {
            this.socket = socket;
        }

        public void run() {
            try {
                in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                out = new PrintWriter(socket.getOutputStream(), true);

                while (true) {
                    nick = in.readLine();
                    if (nick == null || nick.isEmpty() || nick.equals("quit")) {
                        out.println("INVALIDNICK");
                        continue;
                    }
                    synchronized (clients) {
                        if (!clients.containsKey(nick)) {
                            clients.put(nick, out);
                            out.println("NICKACCEPTED");
                            break;
                        } else {
                            out.println("INVALIDNICK");
                        }
                    }
                }


                for (PrintWriter writer : clients.values()) {
                    if (writer != out) {
                        writer.println("MESSAGE " + nick + " has joined");
                    }
                }

                String input;
                while ((input = in.readLine()) != null) {
                    for (Map.Entry<String, PrintWriter> entry : clients.entrySet()) {
                        PrintWriter writer = entry.getValue();
                        if (writer != out) { // Exclude the sender
                            writer.println("MESSAGE FROM " + nick + ": " + input);
                        }
                    }
                }
            } catch (IOException e) {
                System.out.println(e);
            } finally {
                if (nick != null && out != null) {
                    clients.remove(nick);
                    for (PrintWriter writer : clients.values()) {
                        if (writer != out) { // Exclude the sender
                            writer.println("MESSAGE " + nick + " has left");
                        }
                    }
                }
                try {
                    socket.close();
                } catch (IOException e) {
                    System.out.println("Couldn't close a socket, what's going on?");
                }
            }
        }
    }

    private static void startUdpThread() {
        new Thread(() -> {
            try (DatagramSocket socket = new DatagramSocket(PORT)) {
                byte[] buf = new byte[1024];
                while (true) {
                    DatagramPacket packet = new DatagramPacket(buf, buf.length);
                    socket.receive(packet);
                    InetSocketAddress clientAddress = new InetSocketAddress(packet.getAddress(), packet.getPort());

                    clientAddresses.add(clientAddress);

                    String received = new String(packet.getData(), 0, packet.getLength()).trim();
                    if (!received.isEmpty()) {
                        broadcastUdpMessage(clientAddress, received);
                    }
                }
            } catch (IOException e) {
                System.out.println("UDP Thread IOException: " + e.getMessage());
            }
        }).start();
    }

    private static void broadcastUdpMessage(InetSocketAddress senderAddress, String message) {
        clientAddresses.forEach(clientAddress -> {
            if (!clientAddress.equals(senderAddress)) {
                try (DatagramSocket ds = new DatagramSocket()) {
                    byte[] buffer = message.getBytes();
                    DatagramPacket packet = new DatagramPacket(buffer, buffer.length, clientAddress.getAddress(), clientAddress.getPort());
                    ds.send(packet);
                } catch (IOException e) {
                    System.out.println("Error sending UDP message: " + e.getMessage());
                }
            }
        });
    }




}
