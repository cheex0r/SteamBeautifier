import argparse
import base64
import os
import platform
import uuid
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    def __init__(self, salt=None):
        self.backend = default_backend()
        self.salt = salt
        if not self.salt:
            self.salt = EncryptionManager.generate_salt()


    @staticmethod
    def generate_salt(length=16):
        return urlsafe_b64encode(os.urandom(length)).decode('utf-8')


    def get_salt(self):
        return self.salt


    def encrypt(self, plaintext):
        machine_identifier = self._get_machine_identifier()
        key = self._derive_key(machine_identifier)
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        encrypted_data = iv + ciphertext
        encoded_encryption = base64.b64encode(encrypted_data).decode('utf-8')
        return encoded_encryption


    def decrypt(self, encoded_encryption):
        machine_identifier = self._get_machine_identifier()
        key = self._derive_key(machine_identifier)
        encrypted_data = base64.b64decode(encoded_encryption)
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode('utf-8')


    def _get_machine_identifier(self):
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 2*6, 8)][::-1])
        hostname = platform.node()
        machine_identifier = f"{mac_address}-{hostname}"
        return machine_identifier


    def _derive_key(self, machine_identifier):
        # Ensure salt is a string for padding
        salt_str = self.salt.decode('utf-8') if isinstance(self.salt, bytes) else self.salt
        
        # Add padding if necessary
        missing_padding = len(salt_str) % 4
        if missing_padding:
            salt_str += '=' * (4 - missing_padding)
        
        salt = urlsafe_b64decode(salt_str)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        key = kdf.derive(machine_identifier.encode())
        return key


def main():
    parser = argparse.ArgumentParser(description="Encrypt or Decrypt Config Data")
    parser.add_argument("mode", choices=["encrypt", "decrypt"], help="Mode: 'encrypt' to encrypt data, 'decrypt' to decrypt data")
    parser.add_argument("data", help="The data to encrypt or decrypt")
    parser.add_argument("--salt", required=True, help="Salt value for encryption and decryption")

    args = parser.parse_args()

    salt = args.salt.encode('utf-8')
    encryption_manager = EncryptionManager(salt=salt)

    if args.mode == "encrypt":
        encrypted_data = encryption_manager.encrypt(args.data)
        print(f"Encrypted and Base64-encoded data: {encrypted_data}")
    elif args.mode == "decrypt":
        decrypted_data = encryption_manager.decrypt(args.data)
        print(f"Decrypted data: {decrypted_data}")


if __name__ == "__main__":
    main()
