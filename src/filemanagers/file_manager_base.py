import json
import os

from config.encryption_manager import EncryptionManager


class FileManagerBase:
    def __init__(self, filename, encryption_fields=[]):
        self.filename = filename
        self.encryption_fields = encryption_fields


    def load_or_create_file(self, default_data = {}):
        if not os.path.exists(self._get_file_path()):
            return self.save_file(default_data)
        return self.load_file()


    def save_file(self, data):
        with open(self._get_file_path(), 'w') as file:
            json.dump(data, file, indent=4)
        return data
        

    def load_file(self):
        file_path = self._get_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f"Loaded file: {file_path}")

            salt = data.get('encryption_salt', None)
            # Decrypt all encrypted fields
            if salt:
                for field in data.get('_encrypted_fields', []):
                    if field in data:
                        data[field] = self._decrypt(data[field], salt)
        else:
            data = None
        return data


    def _get_file_path(self):
        if os.name == 'nt':  # Windows
            return os.path.join(os.getenv('APPDATA'), 'Steam Beautifier', self.filename)
        else:  # Linux and other OS
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), self.filename)


    def _save_preferences(self, data):
        if data.get('encryption_salt') is None and len(self.encryption_fields) > 0:
            data['encryption_salt'] = EncryptionManager.generate_salt()

        # Encrypt all fields that need to be encrypted
        data_out = data.copy()
        for field in self.encryption_fields:
            if field in data:
                data_out[field] = self._encrypt(data[field], salt=data['encryption_salt'])

        data_out['_encrypted_fields'] = self.ENCRYPTED_FIELDS  # Store the list of encrypted fields
        config_path = self._get_config_path()
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(data_out, f, indent=4)
        return config_path
    

    def _encrypt(self, data, salt):
        return EncryptionManager(salt=salt).encrypt(data)


    def _decrypt(self, data, salt):
        return EncryptionManager(salt=salt).decrypt(data)
