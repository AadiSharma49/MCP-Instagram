import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyAFWdDXuJEEVy4ljceXGwW0yQtIuJnxb44",
    "authDomain": "mcp-serve-11875.firebaseapp.com",
    "databaseURL": "https://mcp-serve-11875-default-rtdb.firebaseio.com",
    "projectId": "mcp-serve-11875",
    "storageBucket": "mcp-serve-11875.firebasestorage.app",
    "messagingSenderId": "466301107002",
    "appId": "1:466301107002:web:b6cdb362e3865b07d66e03",
    "measurementId": "G-J6ZCG42KQF"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

def signup_user(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return user
    except Exception as e:
        raise Exception(f"Signup error: {str(e)}")

def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        raise Exception(f"Login error: {str(e)}")

def save_user_profile(uid, email, insta_username):
    data = {
        "email": email,
        "instagram_username": insta_username
    }
    db.child("users").child(uid).set(data)
