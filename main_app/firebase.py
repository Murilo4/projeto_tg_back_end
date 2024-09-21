import firebase_admin
from firebase_admin import credentials

# Inicialize o Firebase Admin SDK
cred = credentials.Certificate('caminho/para/seu/arquivo/firebase-adminsdk.json')
firebase_admin.initialize_app(cred)