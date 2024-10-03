import firebase_admin
from firebase_admin import credentials

# Inicialize o Firebase Admin SDK
cred = credentials.Certificate('')
firebase_admin.initialize_app(cred)
