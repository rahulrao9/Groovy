import firebase_admin
from firebase_admin import credentials, firestore, auth
import pyrebase
import streamlit as st
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Firebase configuration from environment variables
def get_firebase_config():
    """Get Firebase configuration from environment variables."""
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID")
    }

# Initialize Firebase Admin SDK (for server-side operations)
def initialize_firebase_admin():
    """Initialize Firebase Admin SDK using environment variables."""
    if not firebase_admin._apps:
        try:
            # Use environment variables directly
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
            })
            firebase_admin.initialize_app(cred)
            print("Initialized Firebase Admin SDK with environment variables")
        except Exception as e:
            print(f"Error initializing Firebase Admin SDK with environment variables: {e}")
            print("Please ensure your .env file contains all required Firebase credentials")

# Initialize Pyrebase (for auth and user operations)
def initialize_firebase_client():
    """Initialize Firebase client SDK."""
    config = get_firebase_config()
    return pyrebase.initialize_app(config)

# Get Firestore database
def get_firestore_db():
    """Get Firestore database client."""
    initialize_firebase_admin()
    return firestore.client()

# Initialize on module load
initialize_firebase_admin()
firebase = initialize_firebase_client()
pb_auth = firebase.auth()
db = get_firestore_db()

# Authentication Functions
def sign_up(email, password, username):
    """Create a new user account in Firebase and initialize Firestore documents."""
    try:
        # Create user in Firebase Auth
        user = auth.create_user(
            email=email, 
            password=password,
            display_name=username
        )
        
        # Initialize user document in Firestore
        db.collection('users').document(user.uid).set({
            'email': email,
            'username': username,
            'created_at': firestore.SERVER_TIMESTAMP,
            'total_plays': 0
        })
        
        # Initialize plays collection
        db.collection('users').document(user.uid).collection('plays').document('info').set({
            'initialized': True
        })
        
        return True, user.uid
    except Exception as e:
        return False, str(e)

def sign_in(email, password):
    """Sign in a user with Firebase Auth."""
    try:
        user = pb_auth.sign_in_with_email_and_password(email, password)
        account_info = pb_auth.get_account_info(user['idToken'])
        return True, user['idToken'], account_info['users'][0]['localId']
    except Exception as e:
        return False, None, str(e)

def get_user_info(user_id):
    """Get user info from Firestore."""
    return db.collection('users').document(user_id).get().to_dict()

def update_play_count(user_id, song_id, artist, song_name):
    """Update the play count for a specific song for a user."""        
    # Update song document in user's plays collection
    play_ref = db.collection('users').document(user_id).collection('plays').document(song_id)
    
    # Check if document exists
    doc = play_ref.get()
    if doc.exists:
        # Increment play count
        play_ref.update({
            'count': firestore.Increment(1),
            'last_played': firestore.SERVER_TIMESTAMP
        })
    else:
        # Create new play record
        play_ref.set({
            'song_id': song_id,
            'artist': artist,
            'song': song_name,
            'count': 1,
            'first_played': firestore.SERVER_TIMESTAMP,
            'last_played': firestore.SERVER_TIMESTAMP
        })
    
    # Update total plays count for user
    db.collection('users').document(user_id).update({
        'total_plays': firestore.Increment(1)
    })

def get_user_play_counts(user_id):
    """Get all play counts for a specific user."""
    plays = db.collection('users').document(user_id).collection('plays').get()
    return {doc.id: doc.to_dict() for doc in plays if doc.id != 'info'}

def get_all_users_play_data(limit=50):
    """Get play data across all users (for collaborative filtering)"""
    users = db.collection('users').limit(limit).get()
    all_plays = {}
    
    for user in users:
        user_id = user.id
        plays = get_user_play_counts(user_id)
        all_plays[user_id] = plays
    
    return all_plays 