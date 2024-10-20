from base64 import b64encode
from Cryptodome.Random import get_random_bytes


if __name__ == "__main__":
    key = get_random_bytes(16)
    key_b64 = b64encode(key)
    print(key_b64.decode("UTF-8"))