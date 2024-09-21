import random

def generate_confirmation_code():
    return ''.join(random.choices('123456789', k=6))