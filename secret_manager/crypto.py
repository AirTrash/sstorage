from Cryptodome.Cipher import AES
import logging

from secret_manager.errors import DecryptError


def encrypt(data: bytes, key: bytes) -> (bytes, bytes, bytes):
    cipher = AES.new(key, AES.MODE_OCB)
    cipher.update(b"header")
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return ciphertext, cipher.nonce, tag


def decrypt(data: bytes, key: bytes, nonce, tag: bytes) -> bytes | None:
    cipher = AES.new(key, AES.MODE_OCB, nonce=nonce)
    cipher.update(b"header")
    try:
        plaintext = cipher.decrypt_and_verify(data, tag)
        return plaintext
    except (ValueError, KeyError):
        raise DecryptError
