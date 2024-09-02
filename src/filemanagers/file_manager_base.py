import json
import os

from config.encryption_manager import EncryptionManager


class FileManagerBase:
    def __init__(self, filename, encryption_fields=[]):
        self.filename = filename
        self.encryption_fields = encryption_fields


    def load_or_create_file(self, default_data = None):
        if default_data is None:
            default_data = {}
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
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file: {e}")
                return None
            except IOError as e:
                print(f"Error reading file: {e}")
                return None
            if data is None:
                print("No data loaded; returning None.")
                return None
            salt = data.get('encryption_salt', None)
            # Decrypt all encrypted fields
            if salt:
                encrypted_fields = data.get('_encrypted_fields', [])
                for field in encrypted_fields:
                    if field in data:
                        try:
                            data[field] = self._decrypt(data[field], salt)
                        except Exception as e:
                            print(f"Error decrypting field {field}: {e}")
                            data[field] = None  # or handle decryption error as needed
            return data
        else:
            print(f"File not found: {file_path}")
            return None


    def _get_file_path(self):
        if os.name == 'nt':  # Windows
            base_path = os.path.join(os.getenv('APPDATA'), 'Steam Beautifier')
        else:  # Linux and other OS
            # Linux: Use XDG_CONFIG_HOME or fallback to ~/.config
            base_path = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))
            base_path = os.path.join(base_path, 'SteamBeautifier')
        os.makedirs(base_path, exist_ok=True)
        return os.path.join(base_path, self.filename)


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
