import random
import hashlib
import time

def generate_confirmation_code():
    return ''.join(random.choices('123456789', k=6))

def make_custom_token(user):
    timestamp = str(int(time.time()))
    hash_string = f"{user.pk}-{timestamp}"
    token = hashlib.sha256(hash_string.encode()).hexdigest()
    return f"{token}-{timestamp}"