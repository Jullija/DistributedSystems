import ray
import random
import StorageNode

@ray.remote
class NameNode:
    def __init__(self):
        self.artifacts_metadata = {}
        self.storage_nodes = {}
        self.node_counter = 0

    def register_storage_node(self):
        node_id = self.node_counter
        new_node = StorageNode.remote(node_id)
        self.storage_nodes[node_id] = new_node
        self.node_counter += 1
        return node_id

    def upload_artifact(self, artifact_name, content, replication_factor=2):
        chunk_size = 1024  # Example chunk size
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        self.artifacts_metadata[artifact_name] = []
        for chunk_id, chunk in enumerate(chunks):
            stored_nodes = []
            for _ in range(replication_factor):
                node_id, storage_node = random.choice(list(self.storage_nodes.items()))
                ray.get(storage_node.store_chunk.remote(f"{artifact_name}_{chunk_id}", chunk))
                stored_nodes.append(node_id)
            self.artifacts_metadata[artifact_name].append((chunk_id, stored_nodes))
        return True

    def list_status(self):
        status = {}
        for artifact_name, chunks_info in self.artifacts_metadata.items():
            status[artifact_name] = {}
            for chunk_id, nodes in chunks_info:
                status[artifact_name][chunk_id] = nodes
        return status