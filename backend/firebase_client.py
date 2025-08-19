import firebase_admin
from firebase_admin import credentials, db

# Path to your downloaded Firebase service account key
cred = credentials.Certificate("firebase_config/serviceAccountKey.json")

# Initialize Firebase Admin SDK
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mcp-serve-11875-default-rtdb.firebaseio.com/'
})

print("✅ Firebase Admin initialized successfully")
