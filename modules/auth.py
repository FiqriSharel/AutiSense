import bcrypt
import uuid
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database import get_users_collection

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def register_user(email, password):
    users = get_users_collection()
    if users.find_one({"email": email}):
        return False, "An account with this email already exists."
    user = {
        "user_id": str(uuid.uuid4()),
        "email": email,
        "password_hash": hash_password(password),
        "role": "caregiver",
        "created_at": datetime.utcnow()
    }
    users.insert_one(user)
    return True, "Account created successfully!"

def login_user(email, password):
    users = get_users_collection()
    user = users.find_one({"email": email})
    if not user:
        return False, "No account found with this email."
    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password."
    return True, user