from cryptography.fernet import Fernet
import argparse
import os
import sys


def create_key(key_path):
    """Generate new fernet key 
    :key_path: path where key will be saved (str)
    """
    key = Fernet.generate_key()
    if os.path.exists(key_path):
        print("[!] key already exists")
    else:
        with open(key_path, "wb") as f:
            f.write(key)
        print("[+] key generated")


def get_key(key_path):
    """Gather key 
    :key_path: path of key generated from create_key() (str)
    """
    try:
        key = open(key_path, "rb").read()
        return key
    except:
        print("[!] unable to load key")


def encrypt_data(file, key):
    """Encrypt data passed
    :file: path of file to encrypt (str)
    :key: key generated from get_key() (bytes)
    """
    fernet_key = Fernet(key)
    try:
        with open(file, "rb") as f:
            original_file = f.read()
        encrypted_file = fernet_key.encrypt(original_file)
        with open(file, "wb") as f:
            f.write(encrypted_file)
        print(f"[+] encrypted: {file}")
    except:
        print(f"[!] unable to encrypt: {file}")


def decrypt_data(file, key):
    """Decrypt data passed
    :file: path of file to decrypt (str)
    :key: key generated from get_key() (bytes)
    """
    fernet_key = Fernet(key)
    try:
        with open(file, "rb") as f:
            encrypted_file = f.read()
        decrypted_file = fernet_key.decrypt(encrypted_file)
        with open(file, "wb") as f:
            f.write(decrypted_file)
        print(f"[+] decrypted: {file}")
    except:
        print(f"[!] unable to decrypt: {file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--create_key", metavar="", type=str,
                        help="create key file and save to specified path")
    parser.add_argument("-k", "--key", type=str, metavar="",
                        help="path where key is saved")
    parser.add_argument("-e", "--encrypt", type=str, metavar="",
                        help="path of file to encrypt")
    parser.add_argument("-d", "--decrypt", type=str, metavar="",
                        help="path of file to decrypt")

    if len(sys.argv) <= 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if args.create_key:
        create_key(key_path=args.create_key)

    else:
        key = get_key(args.key)
        if args.encrypt:
            encrypt_data(args.encrypt, key)
        if args.decrypt:
            decrypt_data(args.decrypt, key)
        if args.encrypt and args.decrypt:
            print("[!] choose -e or -d, not both")

