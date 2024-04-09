import ray
import random

@ray.remote
class StorageNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.chunks = {}

    def store_chunk(self, chunk_id, chunk_content):
        self.chunks[chunk_id] = chunk_content
        return True

    def retrieve_chunk(self, chunk_id):
        return self.chunks.get(chunk_id, None)