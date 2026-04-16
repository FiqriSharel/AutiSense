import uuid
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from database import get_children_collection

FOCUS_AREAS = [
    "Communication",
    "Social Interaction",
    "Behaviour",
    "Sensory",
    "Emotional Regulation"
]

def create_child_profile(user_id, name, age, focus_areas):
    children = get_children_collection()
    child = {
        "child_id": str(uuid.uuid4()),
        "user_id": user_id,
        "name": name,
        "age": age,
        "focus_areas": focus_areas,
        "created_at": datetime.utcnow()
    }
    children.insert_one(child)
    return True, "Child profile created successfully!"

def get_user_children(user_id):
    children = get_children_collection()
    return list(children.find({"user_id": user_id}))

def update_child_profile(child_id, name, age, focus_areas):
    children = get_children_collection()
    children.update_one(
        {"child_id": child_id},
        {"$set": {
            "name": name,
            "age": age,
            "focus_areas": focus_areas,
            "updated_at": datetime.utcnow()
        }}
    )
    return True, "Profile updated successfully!"

def delete_child_profile(child_id):
    children = get_children_collection()
    children.delete_one({"child_id": child_id})
    return True, "Profile deleted."