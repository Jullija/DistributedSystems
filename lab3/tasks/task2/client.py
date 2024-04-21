import ray
from nameNode import NameNode
from dataNode import DataNode
import asyncio

# Start Ray
ray.init()

class NameNodeClient:
    def __init__(self):
        self.name_node = None
        
    
    def start_name_node(self):
        self.name_node = NameNode.remote()
        print("NameNode started.")
    
    def add_data_node(self):
        if self.name_node:
            try:
                data_node = DataNode.remote()
                ray.get(self.name_node.add_data_node.remote(data_node))
                print("Data node added successfully.")
            except ValueError:
                print("couldn't create artifact, possibly name repeats")
                
        else:
            print("NameNode is not initialized.")

    async def add_artifact(self, artifact_name, data):
        if self.name_node:
            try:
                await self.name_node.add_artifact.remote(artifact_name, data)
                print(f"Artifact '{artifact_name}' added successfully.")
            except ValueError:
                print("couldn't create artifact, possibly name repeats")
        else:
            print("NameNode is not initialized.")
            
    async def update_artifact(self, artifact_name, data):
        if self.name_node:
            await self.name_node.update_artifact.remote(artifact_name, data)
            print(f"Artifact '{artifact_name}' updated successfully.")
        else:
            print("NameNode is not initialized.")

    def delete_artifact(self, artifact_name):
        if self.name_node:
            self.name_node.delete_artifact.remote(artifact_name)
            print(f"Artifact '{artifact_name}' deleted successfully.")
        else:
            print("NameNode is not initialized.")

    def download_artifact(self, artifact_name):
        if self.name_node:
            data = ray.get(self.name_node.download_artifact.remote(artifact_name))
            print(f"Artifact '{artifact_name}' downloaded successfully.")
            print(f"{data}")
        else:
            print("NameNode is not initialized.")

    def get_node_info(self, node_idx):
        if self.name_node:
            info = ray.get(self.name_node.get_node_info.remote(node_idx))
            print(f"Node {node_idx} info: {info}")
        else:
            print("NameNode is not initialized.")
    
    def get_info(self):
        if self.name_node:
            info = ray.get(self.name_node.get_all_nodes_info.remote())
            print(f"Info:\n{info}")
        else:
            print("NameNode is not initialized.")
            
    def deactivate_node(self, node_idx):
        if self.name_node:
            info = ray.get(self.name_node.deactivate_node.remote(node_idx))
            print(f"Node {node_idx} info: {info}")
        else:
            print("NameNode is not initialized.")

async def main_loop():
    client = NameNodeClient()
    client.start_name_node()
    for _ in range(3):
        client.add_data_node()

    while True:
        command = input("Enter command (add_data_node, add, delete, update, download get_node_info, get_info, exit): ")
        if command == "add_data_node":
            client.add_data_node()
        elif command.startswith("add"):
            parts = command.split(maxsplit=2)
            if len(parts) >= 3:
                artifact_name, data = parts[1], parts[2]
                await client.add_artifact(artifact_name, data)
            else:
                print("Usage: add <name> <data>")
        elif command.startswith("update"):
            parts = command.split(maxsplit=2)
            if len(parts) >= 3:
                artifact_name, data = parts[1], parts[2]
                await client.update_artifact(artifact_name, data)
            else:
                print("Usage: update <name> <new_data>")
        elif command.startswith("get_node_info"):
            parts = command.split()
            if len(parts) == 2 and parts[1].isdigit():
                node_idx = int(parts[1])
                client.get_node_info(node_idx)
            else:
                print("Usage: get_node_info <node_index>")
        elif command.startswith("deactivate"):
            parts = command.split()
            if len(parts) == 2 and parts[1].isdigit():
                node_idx = int(parts[1])
                client.deactivate_node(node_idx)
            else:
                print("Usage: deactivate <node_index>")
        elif command.startswith("delete"):
            parts = command.split()
            if len(parts) == 2:
                client.delete_artifact(parts[1])
            else:
                print("Usage: delete <artifact_name>")
        elif command.startswith("download"):
            parts = command.split()
            if len(parts) == 2:
                client.download_artifact(parts[1])
            else:
                print("Usage: download <artifact_name>")
        elif command.startswith("get_info"):
            client.get_info()
        elif command == "exit":
            print("Exiting...")
            break
        else:
            print("Invalid command. Use 'add_data_node', 'add_artifact', 'get_node_info', or 'exit'.")

if __name__ == "__main__":
    asyncio.run(main_loop())
