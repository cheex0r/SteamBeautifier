import json
import os

class AppData:
    @classmethod
    def get_path(cls):
        if os.name == 'nt':  # Windows
            return os.path.join(os.getenv('APPDATA'), 'Steam Beautifier')
        else:  # Linux and other OS
            return os.path.join(os.path.dirname(os.path.abspath(__file__)))

    @classmethod        
    def get_file_path(cls, filename):
        path = cls.get_path()
        return os.path.join(path, filename)
    
    @classmethod
    def read_json_from_file(cls, file_name, collection_type=list):
        file_path = cls.get_file_path(file_name)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as file:
                    return collection_type(json.load(file))
            except Exception as e:
                pass
                # print(f"An error occurred while reading the file {file_name}: {e}")
        else:
            pass
            # print(f"File {file_name} does not exist.")
        return collection_type()
    
    @classmethod
    def save_json_to_file(cls, file_name, data, collection_type=list):
        file_path = cls.get_file_path(file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            if isinstance(data, set):
                data = list(data)  # Convert set to list before saving
            json.dump(collection_type(data), f, indent=4)
