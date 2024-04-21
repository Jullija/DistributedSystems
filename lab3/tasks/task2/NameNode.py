import asyncio
import threading
import ray
from random import sample, choice

CHUNK_SIZE = 20



def divide_into_chunks(artifact_data):
    length_of_data = len(artifact_data)
    number_of_chunks = (length_of_data + CHUNK_SIZE - 1) // CHUNK_SIZE
    
    chunks = {}
    for i in range(number_of_chunks):
        start_index = i * CHUNK_SIZE
        end_index = min(start_index + CHUNK_SIZE, length_of_data)
        chunk_data = artifact_data[start_index:end_index]
        chunks[i] = chunk_data
    
    return chunks


@ray.remote
class NameNode():
    def __init__(self, num_copies=2):
        self.num_copies = num_copies
        self.artifacts_chunks_positions = {}
        self.artifacts_num_chunks = {}
        self.data_nodes = []
        self.deactivated_nodes = []
        
        loop = asyncio.new_event_loop()
        self.start_async_monitoring()

    def start_async_monitoring(self):
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.monitor_nodes())

        thread = threading.Thread(target=run_async)
        thread.start()

        
    def add_data_node(self, data_node):
        self.data_nodes.append(data_node)
        
    async def add_artifact(self, artifact_name, data):
        chunks = divide_into_chunks(data)
        self.artifacts_num_chunks[artifact_name] = len(chunks)
        
        results = await asyncio.gather(*(node.is_available.remote() for node in self.data_nodes))

        allowed_nodes = [self.data_nodes[i] for i, is_available in enumerate(results) if is_available]
        if artifact_name in self.artifacts_chunks_positions:
            raise ValueError("Artifact already added")
        
        self.artifacts_chunks_positions[artifact_name] = {}
        
        for chunk_id, chunk_data in chunks.items():
            if not allowed_nodes:
                raise Exception("No available nodes to store chunks.")
            chosen_nodes = sample(allowed_nodes, self.num_copies)
            self.artifacts_chunks_positions[artifact_name][chunk_id] = []
            for node in chosen_nodes:
                node.add_chunk.remote(artifact_name, chunk_id, chunk_data)
                self.artifacts_chunks_positions[artifact_name][chunk_id].append(node)

                
    def delete_artifact(self, artifact_name):
        if artifact_name not in self.artifacts_chunks_positions.keys():
            raise ValueError("Artifact with this name doesn't exist")
        
        artifact_chunks_positions = self.artifacts_chunks_positions[artifact_name]
        
        for chunk_id in artifact_chunks_positions.keys():
            for node in artifact_chunks_positions[chunk_id]:
                node.delete_artifact.remote(artifact_name)
        self.artifacts_chunks_positions.pop(artifact_name)
        self.artifacts_num_chunks.pop(artifact_name)

    async def update_artifact(self, artifact_name, new_data):
        self.delete_artifact(artifact_name)
        await self.add_artifact(artifact_name, new_data)
        
    
    async def download_artifact(self, artifact_name):
        artifact_nodes = self.artifacts_chunks_positions[artifact_name]
        total_chunks = self.artifacts_num_chunks[artifact_name]

        chunks = []
        object_refs = []
        
        for chunk_id, nodes in artifact_nodes.items():
            if len(nodes) == 0:
                raise Exception("Lost chunks")
            node_to_use = choice(nodes) 
            object_refs.append(node_to_use.get_chunk.remote(artifact_name, chunk_id))

        chunk_data = await asyncio.gather(*object_refs)

        chunks = [(chunk_id, data) for (chunk_id, _), data in zip(artifact_nodes.items(), chunk_data)]
        
        chunks.sort(key=lambda x: x[0])

        result = "".join(chunk[1] for chunk in chunks)
        return result

    async def get_node_info(self, node_idx):
        print(f"DataNode {node_idx}:")
        if node_idx >= 0 and node_idx < len(self.data_nodes):
            return await self.data_nodes[node_idx].get_info.remote()
        
    async def get_all_nodes_info(self):
        info_refs = [node.get_info.remote() for node in self.data_nodes]
        infos = await asyncio.gather(*info_refs)

        result = ""
        for i, info in enumerate(infos):
            result += f"DataNode {i}:\n"
            result += "\n     " + "\n     ".join(info.split("\n"))
            result += "\n"
        return result
    
    async def deactivate_node(self, node_idx):
        if node_idx >= 0 and node_idx < len(self.data_nodes):
            await self.data_nodes[node_idx].disable.remote()


    async def monitor_nodes(self):
        while True:
            availability = await asyncio.gather(*(node.is_available.remote() for node in self.data_nodes))
            for i, is_available in enumerate(availability):
                if not is_available and self.data_nodes[i] not in self.deactivated_nodes:
                    self.deactivated_nodes.append(self.data_nodes[i])
                    await self.redistribute_chunks(i)
            await asyncio.sleep(5)


    async def redistribute_chunks(self, node_idx):
        print(f"Handling deactivated node: {node_idx}")
        flawed_node = self.data_nodes[node_idx]
        for artifact, chunks in self.artifacts_chunks_positions.items():
            for chunk_id, nodes in chunks.items():
                if flawed_node in nodes:
                    nodes.remove(flawed_node)
                    if nodes:  
                        copy_node = choice(nodes)
                        data = await copy_node.get_chunk.remote(artifact, chunk_id) 

                        availability = await asyncio.gather(*(n.is_available.remote() for n in self.data_nodes))
                        available_nodes = [n for n, available in zip(self.data_nodes, availability) if available and n not in nodes]
                        
                        if available_nodes:
                            new_node = choice(available_nodes)
                            await new_node.add_chunk.remote(artifact, chunk_id, data)
