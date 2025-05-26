import json
import os
import uuid
from datetime import datetime, timedelta
from database.db import DB
from Crypto.Cipher import AES
import zlib
import base64
import hashlib

def unlock_file(info, response):
    """
        Unlocks an encrypted file associated with a user and generates a temporary shareable download link.

        Args:
            info (dict): A dictionary containing request data, including cookies and request body.
            response (dict): A dictionary to store the HTTP response body, headers, and code.

        Returns:
            dict: The updated response dictionary containing either the download link and cookie information, 
                or an error message and status code.
    """
    try:
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        db_path = os.path.join(os.getcwd(), "web-server", "database", "data.sqlite")
        database_access = DB(db_path)

        user_id = database_access.check_cookie(auth_cookie_value)

        body_data = json.loads(info["body"])
        server_key = body_data["server_key"]
        password = body_data["password"]
        
        metadata = database_access.get_metadata(server_key, user_id)
        name = metadata[4]

    except Exception as e:
        response["body"] = json.dumps({"failed": "missing info or invalid cookie", "message": str(e)})
        response["headers"] = {"Content-Type": "application/json"}
        response["response_code"] = "400"
        return response

    try:
        file_path = os.path.join("web-server", "database", "files", user_id, f"{server_key}.txt")
        if not os.path.exists(file_path):
            raise FileNotFoundError("Encrypted file not found")

        with open(file_path, "r", encoding="utf-8") as file:
            encrypted_chunks = file.read().splitlines()

        decrypted_chunks = []
        for chunk in encrypted_chunks:
            if not chunk.strip():
                continue
            decrypted_data = decrypt_and_decompress_chunk(chunk.strip(), password)
            decrypted_chunks.append(decrypted_data)

        final_content = b''.join(decrypted_chunks)

        
        share_cookie = database_access.create_cookie(user_id, "share_cookie")
        
        decrypted_name = decrypt_string(name, password)
        file_extension = decrypted_name.split('.')[-1]
        temp_file_id = f"{share_cookie[1]}.{file_extension}"
        temp_dir = os.path.join("web-server", "tempdata")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, f"{temp_file_id}")

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(final_content)


        share_link = f"https://a9035.kcyber.net/share/{temp_file_id}"
        response["headers"]["Content-Type"] = "application/json"
        response["body"] = json.dumps({
            "success": True,
            "share_link": share_link,
            "cookie": {
                "key": share_cookie[0],
                "value": share_cookie[1],
                "expires": share_cookie[2]
            }
        })
        response["response_code"] = "200"

    except Exception as e:
        response["body"] = json.dumps({"failed": "couldn't unlock file", "message": str(e)})
        response["response_code"] = "500"

    return response

def evp_kdf(password, salt, key_size=32, iv_size=16):
    """
    Derives a key and IV from a password and salt using OpenSSL-compatible EVP_BytesToKey method (MD5-based).

    Args:
        password (bytes): The password used for key derivation.
        salt (bytes): The salt used in derivation (8 bytes).
        key_size (int): Desired length of the key in bytes. Default is 32.
        iv_size (int): Desired length of the IV in bytes. Default is 16.

    Returns:
        tuple: A tuple containing the derived key and IV.
    """
    d = b''
    while len(d) < key_size + iv_size:
        d_i = hashlib.md5(d[-16:] + password + salt) if d else hashlib.md5(password + salt)
        d += d_i.digest()
    return d[:key_size], d[key_size:key_size+iv_size]

def pad(data: bytes, block_size=16):
    """
    Pads the input data to a multiple of the block size using PKCS7 padding.

    Args:
        data (bytes): The data to be padded.
        block_size (int): The block size to pad to. Default is 16 bytes.

    Returns:
        bytes: The padded data.
    """
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)

def unpad(data: bytes):
    """
    Removes PKCS7 padding from the data.

    Args:
        data (bytes): The padded data.

    Returns:
        bytes: The unpadded original data.
    """
    pad_len = data[-1]
    return data[:-pad_len]

def decrypt_string(encrypted_b64: str, password: str) -> str:
    """
    Decrypts a base64-encoded AES-encrypted string using a password and salt.

    The encryption must have used OpenSSL-compatible format with "Salted__" header.

    Args:
        encrypted_b64 (str): The base64-encoded encrypted string.
        password (str): The password used for decryption.

    Returns:
        str: The decrypted string.
    """
    encrypted = base64.b64decode(encrypted_b64)
    assert encrypted[:8] == b"Salted__", "Invalid header"
    salt = encrypted[8:16]
    ciphertext = encrypted[16:]
    key, iv = evp_kdf(password.encode(), salt)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded = cipher.decrypt(ciphertext)
    decrypted = unpad(decrypted_padded)
    return decrypted.decode('utf-8')

def decrypt_and_decompress_chunk(encrypted_chunk: str, key: str) -> bytes:
    """
    Decrypts a single base64-encoded chunk of data using AES and decompresses it using zlib.

    The chunk must have been encrypted using OpenSSL-compatible AES with "Salted__" format and 
    then double base64-encoded (first for encryption, then after compression).

    Args:
        encrypted_chunk (str): The encrypted and base64-encoded string chunk.
        key (str): The password used for AES decryption.

    Returns:
        bytes: The decompressed binary data of the original chunk.

    Raises:
        Exception: If decryption or decompression fails.
    """
    try:
        encrypted = base64.b64decode(encrypted_chunk)

        if encrypted[:8] != b"Salted__":
            raise ValueError("Missing OpenSSL salt header")

        salt = encrypted[8:16]
        ciphertext = encrypted[16:]

        key_bytes, iv = evp_kdf(key.encode('utf-8'), salt)

        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)

        pad_len = decrypted[-1]
        decrypted = decrypted[:-pad_len]

        base64_str = decrypted.decode('utf-8')
        raw_binary = base64.b64decode(base64_str)
        return zlib.decompress(raw_binary)

    except Exception as e:
        raise Exception("Decryption or decompression failed") from e