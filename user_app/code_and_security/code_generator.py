import random
import hashlib
import time
import uuid
import jwt
import os
from datetime import datetime, timedelta, timezone
from django.core.cache import cache
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')


def generate_confirmation_code():
    return ''.join(random.choices('123456789', k=6))


def make_custom_token(user):
    timestamp = str(int(time.time()))
    hash_string = f"{user.pk}-{timestamp}"
    token = hashlib.sha256(hash_string.encode()).hexdigest()
    return f"{token}-{timestamp}"


def generate_session_id():
    return str(uuid.uuid4())


def generate_jwt(user_data):
    payload = {
        'id': user_data.id,
        'email': user_data.email,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=10)
        # Define expiração para 10 minutos
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def generate_jwt_session(user_data):
    payload = {
        'id': user_data.id,
        'email': user_data.email,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=10080)
        # Define expiração para 10 minutos
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def blacklist_jwt(token):
    # Calcular o tempo restante de expiração
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"],
                                  options={"verify_exp": False})
        exp_timestamp = decoded_data.get("exp")
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        time_to_expire = (exp_datetime - datetime.now(timezone.utc)
                          ).total_seconds()
        token_hash = hashlib.md5(token.encode()).hexdigest()
        cache.set(f'blacklisted_token_{token_hash}', True,
                  timeout=int(time_to_expire))
    except jwt.InvalidTokenError:
        pass


def is_token_blacklisted(token):
    token_hash = hashlib.md5(token.encode()).hexdigest()
    return cache.get(f'blacklisted_token_{token_hash}') is not None


def validate_jwt(token):
    if is_token_blacklisted(token):
        return {"error": "Token já foi revogado."}
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return {"error": "Token expirado."}
    except jwt.InvalidTokenError:
        return {"error": "Token inválido."}


def extract_email_from_jwt(token):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded_data.get('email')  # Extraindo o email
        return email
    except jwt.ExpiredSignatureError:
        return None  # O token expirou
    except jwt.InvalidTokenError:
        return None  # O token é inválido


def generate_jwt_2(user_data):
    payload = {
        'email': user_data['email'],
        'user_name': user_data['user_name'],
        'nick_name': user_data['nick_name'],
        'exp': datetime.now(timezone.utc) + timedelta(minutes=10)
        # Define expiração para 10 minutos
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
