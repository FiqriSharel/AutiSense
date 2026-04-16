from pymongo import MongoClient
import streamlit as st

@st.cache_resource
def get_database():
    client = MongoClient(st.secrets["MONGO_URI"])
    return client["autisense"]

def get_users_collection():
    return get_database()["users"]

def get_children_collection():
    return get_database()["children"]

def get_observations_collection():
    return get_database()["observations"]

def get_interactions_collection():
    return get_database()["interactions"]

def get_progress_collection():
    return get_database()["progress"]