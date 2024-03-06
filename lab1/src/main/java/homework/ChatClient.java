package homework;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.io.*;
import java.net.*;

public class ChatClient {
    BufferedReader reader;
    PrintWriter writer;
    JFrame frame = new JFrame("Chat");
    JTextField textField = new JTextField(40);
    JTextArea messageArea = new JTextArea(8, 40);
    private static final int PORT = 12345;
    private DatagramSocket udpSocket;
    private InetAddress address;

    public ChatClient() {
        textField.setEditable(false);
        messageArea.setEditable(false);
        frame.getContentPane().add(textField, BorderLayout.NORTH);
        frame.getContentPane().add(new JScrollPane(messageArea), BorderLayout.CENTER);
        frame.pack();

        textField.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                String text = textField.getText();
                if (text.startsWith("U")) {
                    // Remove 'U' and send the rest as a UDP message
                    sendUDPMessage(text.substring(1).trim());
                } else {
                    writer.println(text);
                }
                textField.setText("");
            }
        });
    }

    private String getServerAddress() {
        return JOptionPane.showInputDialog(
                frame,
                "Enter IP Address of the Server:",
                "Welcome to the Chat",
                JOptionPane.QUESTION_MESSAGE);
    }

    private String getName() {
        return JOptionPane.showInputDialog(
                frame,
                "Choose a screen name:",
                "Screen name selection",
                JOptionPane.PLAIN_MESSAGE);
    }

    private void sendUDPMessage(String message) {
        try {
            byte[] buf = message.getBytes();
            DatagramPacket packet = new DatagramPacket(buf, buf.length, address, PORT);
            udpSocket.send(packet);
        } catch (IOException e) {
            System.out.println("IOException: " + e.getMessage());
        }
    }

    private void run() throws IOException {
        String serverAddress = getServerAddress();
        Socket socket = new Socket(serverAddress, PORT);
        reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        writer = new PrintWriter(socket.getOutputStream(), true);

        address = InetAddress.getByName(serverAddress);
        udpSocket = new DatagramSocket();

        while (true) {
            String line = reader.readLine();
            if (line.startsWith("NAME_SUBMITTED")) {
                writer.println(getName());
            } else if (line.startsWith("NAME_ACCEPTED")) {
                textField.setEditable(true);
            } else if (line.startsWith("MESSAGE")) {
                messageArea.append(line.substring(8) + "\n");
            }
        }
    }

    public static void main(String[] args) throws Exception {
        ChatClient client = new ChatClient();
        client.frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        client.frame.setVisible(true);
        client.run();
    }
}
