import firebase_admin
from firebase_admin import credentials
import os
FIREBASE_KEY = os.getenv('FIREBASE_KEY')
# Inicialize o Firebase Admin SDK
cred = credentials.Certificate('FIREBASE_KEY')
firebase_admin.initialize_app(cred)
