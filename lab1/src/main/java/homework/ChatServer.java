package homework;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;

public class ChatServer {
    private static final int PORT = 12345;
    private static ConcurrentHashMap<String, PrintWriter> clients = new ConcurrentHashMap<>();

    public static void main(String[] args) throws Exception {
        System.out.println("Chat Server is running.");
        ServerSocket listener = new ServerSocket(PORT);

        try {
            while (true) {
                new Handler(listener.accept()).start();
            }
        } finally {
            listener.close();
        }
    }

    private static class Handler extends Thread {
        private String name;
        private Socket socket;
        private Scanner scanner; //read from client
        private PrintWriter writer; //write on output

        public Handler(Socket socket) {
            this.socket = socket;
        }

        public void run() {
            try {
                scanner = new Scanner(socket.getInputStream());
                writer = new PrintWriter(socket.getOutputStream(), true);

                while (true) {
                    writer.println("NAME_SUMBITTED");
                    name = scanner.nextLine();
                    if (name == null || name.isEmpty() || clients.containsKey(name)) {
                        continue;
                    }
                    synchronized (clients) {
                        if (!clients.containsKey(name)) {
                            clients.put(name, writer);
                            break;
                        }
                    }
                }

                writer.println("NAME_ACCEPTED " + name);
                for (PrintWriter writer : clients.values()) {
                    writer.println("HEY_HI_HELLO " + name + " has joined");
                }

                while (true) {
                    String input = scanner.nextLine();
                    if (input.toLowerCase().startsWith("/quit")) {
                        return;
                    }
                    for (PrintWriter writer : clients.values()) {
                        writer.println("MESSAGE " + name + ": " + input);
                    }
                }
            } catch (Exception e) {
                System.out.println(e);
            } finally {
                if (name != null) {
                    clients.remove(name);
                    for (PrintWriter writer : clients.values()) {
                        writer.println("MESSAGE " + name + " has left");
                    }
                }
                try { socket.close(); } catch (IOException e) {}
            }
        }
    }
}

