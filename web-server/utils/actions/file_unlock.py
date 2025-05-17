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
    try:
        # Extract auth cookie
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        db_path = os.path.join(os.getcwd(), "web-server", "database", "data.sqlite")
        database_access = DB(db_path)

        # Get user from cookie
        user_id = database_access.check_cookie(auth_cookie_value)

        # Parse request body
        body_data = json.loads(info["body"])
        server_key = body_data["server_key"]
        password = body_data["password"]

    except Exception as e:
        response["body"] = json.dumps({"failed": "missing info or invalid cookie", "message": str(e)})
        response["response_code"] = "500"
        return response

    try:
        # Fetch encrypted file
        file_path = os.path.join("web-server", "database", "files", user_id, f"{server_key}.txt")
        if not os.path.exists(file_path):
            raise FileNotFoundError("Encrypted file not found")

        # Read chunks
        with open(file_path, "r", encoding="utf-8") as file:
            encrypted_chunks = file.read().splitlines()

        # Decrypt and decompress each chunk
        decrypted_chunks = []
        for chunk in encrypted_chunks:
            if not chunk.strip():
                continue
            decrypted_data = decrypt_and_decompress_chunk(chunk.strip(), password)
            decrypted_chunks.append(decrypted_data)

        # Combine all decrypted chunks
        final_content = b''.join(decrypted_chunks)

        # Save to tempdata directory
        temp_file_id = str(uuid.uuid4())
        temp_dir = os.path.join("web-server", "tempdata")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, f"{temp_file_id}.bin")
        print(f"Temp file path: {temp_file_path}")

        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(final_content)

        # Create a short-lived cookie for the share session
        share_cookie = database_access.create_cookie(user_id)

        # Return file share link
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
    """ Derive key and IV from password and salt (OpenSSL EVP_BytesToKey) """
    d = b''
    while len(d) < key_size + iv_size:
        d_i = hashlib.md5(d[-16:] + password + salt) if d else hashlib.md5(password + salt)
        d += d_i.digest()
    return d[:key_size], d[key_size:key_size+iv_size]

def decrypt_and_decompress_chunk(encrypted_chunk: str, key: str) -> bytes:
    try:
        encrypted = base64.b64decode(encrypted_chunk)

        if encrypted[:8] != b"Salted__":
            raise ValueError("Missing OpenSSL salt header")

        salt = encrypted[8:16]
        ciphertext = encrypted[16:]

        key_bytes, iv = evp_kdf(key.encode('utf-8'), salt)

        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)

        # Remove PKCS7 padding
        pad_len = decrypted[-1]
        decrypted = decrypted[:-pad_len]

        # base64 decode and zlib decompress
        base64_str = decrypted.decode('utf-8')
        raw_binary = base64.b64decode(base64_str)
        return zlib.decompress(raw_binary)

    except Exception as e:
        print("Error:", e)
        raise Exception("Decryption or decompression failed") from e