import javax.swing.*;
import java.awt.*;
import java.io.IOException;
import java.util.List;
import org.apache.zookeeper.*;
import org.apache.zookeeper.data.Stat;

import static org.apache.zookeeper.Watcher.Event.EventType.NodeCreated;
import static org.apache.zookeeper.Watcher.Event.EventType.NodeDeleted;

public class ZookeeperTask extends JFrame implements Watcher {

    private static final String ZNODE_PATH = "/a";
    private static String applicationName;
    private static ZooKeeper zooKeeper;
    private static Process externalAppProcess;
    private final String connectString = "localhost:2181,localhost:2182,localhost:2183";
    private JTextArea textArea;

    public ZookeeperTask() {
        super("ZooKeeper Task");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(600, 400);
        setupUI();
        setVisible(true);
        try {
            zooKeeper = new ZooKeeper(connectString, 3000, this);
            refreshWatches(ZNODE_PATH);
        } catch (IOException | KeeperException | InterruptedException e) {
            e.printStackTrace();
        }
    }

    private boolean nodeExists(String path) {
        try {
            return zooKeeper.exists(path, false) != null;
        } catch (KeeperException | InterruptedException e) {
            textArea.append("Error checking node existence: " + e.getMessage() + "\n");
            return false;
        }
    }

    private void setupUI() {
        textArea = new JTextArea();
        textArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(textArea);
        JButton displayTreeButton = new JButton("Display Tree Structure");
        displayTreeButton.addActionListener(e -> {
            textArea.setText("");  // Clear the text area each time before displaying the tree
            if (nodeExists(ZNODE_PATH)) {
                displayChildrenCount();  // Display the count first
                try {
                    textArea.append(buildTreeText(ZNODE_PATH, ""));
                } catch (KeeperException | InterruptedException ex) {
                    textArea.append("Error building tree: " + ex.getMessage() + "\n");
                }
            } else {
                textArea.append("Node /a does not exist.\n");
            }
        });

        JPanel panel = new JPanel();
        panel.setLayout(new BorderLayout());
        panel.add(new JLabel("ZooKeeper Task", SwingConstants.CENTER), BorderLayout.NORTH);
        panel.add(scrollPane, BorderLayout.CENTER);
        panel.add(displayTreeButton, BorderLayout.SOUTH);

        add(panel);
    }

    public static void main(String[] args) {
        if (args.length != 1) {
            System.err.println("Pass <external_application_name>");
            System.exit(1);
        }
        applicationName = args[0];
        SwingUtilities.invokeLater(ZookeeperTask::new);
    }

    private void refreshWatches(String path) throws KeeperException, InterruptedException {
        // Set a watch on the current node
        zooKeeper.exists(path, true);
        List<String> children = zooKeeper.getChildren(path, true);  // Also set watches on children
        for (String child : children) {
            String childPath = path + "/" + child;
            refreshWatches(childPath);  // Recursively set watch on each child
        }
    }

    @Override
    public void process(WatchedEvent event) {
        SwingUtilities.invokeLater(() -> {
            try {
                switch (event.getType()) {
                    case NodeCreated:
                    case NodeDeleted:
                        displayChildrenCount();
                        updateTextArea("Node " + event.getPath() + " " + event.getType().name().toLowerCase().replace("node", "").trim());
                        if (event.getPath().equals(ZNODE_PATH)) {
                            if (event.getType() == NodeCreated) {
                                startExternalApp();
                                zooKeeper.exists(event.getPath(), true);  // Re-set watch specifically
                                refreshWatches(ZNODE_PATH);
                            } else if (event.getType() == NodeDeleted) {
                                stopExternalApp();
                                textArea.append("Node /a deleted, watching for re-creation...\n");
                                zooKeeper.exists(ZNODE_PATH, true); // Re-set watch for creation
                            }
                        }
                        break;
                    case NodeChildrenChanged:
                        displayChildrenCount();
                        if (event.getPath().startsWith(ZNODE_PATH)) {
                            refreshWatches(event.getPath());
                        }
                        break;
                    default:
                        break;
                }
            } catch (KeeperException | InterruptedException e) {
                e.printStackTrace();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
    }

    private void startExternalApp() throws IOException {
        if (externalAppProcess == null) {
            externalAppProcess = new ProcessBuilder(applicationName).start();
            updateTextArea("External application started.");
        }
    }

    private void stopExternalApp() {
        if (externalAppProcess != null) {
            externalAppProcess.destroy();
            externalAppProcess = null;
            updateTextArea("External application stopped.");
        }
    }

    private void displayChildrenCount() {
        SwingUtilities.invokeLater(() -> {
            try {
                int totalChildrenCount = countChildren(ZNODE_PATH);
                textArea.append("Total number of children in the tree rooted at /a: " + totalChildrenCount + "\n");
            } catch (KeeperException | InterruptedException e) {
                textArea.append("Error counting children: " + e.getMessage() + "\n");
            }
        });
    }

    private int countChildren(String path) throws KeeperException, InterruptedException {
        List<String> children = zooKeeper.getChildren(path, false);
        int count = children.size(); // count direct children
        for (String child : children) {
            count += countChildren(path + "/" + child); // recursively count children of children
        }
        return count;
    }

    private static String buildTreeText(String path, String indent) throws KeeperException, InterruptedException {
        StringBuilder treeText = new StringBuilder();
        Stat stat = zooKeeper.exists(path, false);
        if (stat != null) {
            treeText.append(indent).append(path.substring(path.lastIndexOf('/') + 1)).append("\n");
            List<String> children = zooKeeper.getChildren(path, false);
            for (String child : children) {
                treeText.append(buildTreeText(path + "/" + child, indent + "--"));
            }
        }
        return treeText.toString();
    }

    private void updateTextArea(String message) {
        textArea.append(message + "\n");
        try {
            Stat stat = zooKeeper.exists(ZNODE_PATH, false);
            if (stat != null) {
                displayNodeData(ZNODE_PATH);
            }
        } catch (KeeperException | InterruptedException e) {
            textArea.append("Error checking node existence: " + e.getMessage() + "\n");
        }
    }

    private void displayNodeData(String path) {
        try {
            Stat stat = new Stat();
            byte[] data = zooKeeper.getData(path, false, stat);
            if (data != null && data.length != 0) {
                String dataString = new String(data);
                textArea.append("Data at " + path + ": " + dataString + "\n");
            }
        } catch (KeeperException.NoNodeException e) {
            textArea.append("Node " + path + " does not exist.\n");
        } catch (KeeperException | InterruptedException e) {
            textArea.append("Failed to retrieve data from " + path + ": " + e.getMessage() + "\n");
        }
    }
}
