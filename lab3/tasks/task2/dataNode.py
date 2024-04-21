import ray


@ray.remote
class DataNode():
    def __init__(self):
        self.artifacts = {}
        self.is_working = True
    
    
    def get_chunk(self, artifact_name, chunk_id):
        return self.artifacts[artifact_name][chunk_id]
    
    def delete_artifact(self, artifact_name):
        if artifact_name in self.artifacts.keys():
            self.artifacts.pop(artifact_name)
    
    def add_chunk(self, artifact_name, chunk_id, chunk_data):
        if artifact_name not in self.artifacts:
            self.artifacts[artifact_name] = {}
        self.artifacts[artifact_name][chunk_id] = chunk_data
    
    def get_info(self):
        if not self.is_working: return "" 
        result_str = ""
        for artifact in self.artifacts.keys():
            result_str += f"{artifact} chunks: "
            result_str += f"{sorted(list(self.artifacts[artifact].keys()))}"
            result_str += "\n"
        return result_str
    
    def disable(self):
        self.is_working = False
    
    def toggle_availability(self):
        self.is_working = not self.is_working
        
    def is_available(self):
        return self.is_working

    
            
    
    
    