import firebase_admin
from firebase_admin import credentials, firestore, auth
import pyrebase
import streamlit as st
import os
import json

# Firebase configuration
firebaseConfig = {
    "apiKey": "AIzaSyBVK0DSYXEacaTSuIp4FiGgA3aqN3Jjf8Q",
    "authDomain": "groovy-dev-e950b.firebaseapp.com",
    "databaseURL": "https://groovy-dev-e950b-default-rtdb.firebaseio.com",
    "projectId": "groovy-dev-e950b",
    "storageBucket": "groovy-dev-e950b.appspot.com",
    "messagingSenderId": "787286464183",
    "appId": "1:787286464183:web:f631c16167720e76d51f32",
    "measurementId": "G-NYX8NLTY3P"
}

# Initialize Firebase Admin SDK (for server-side operations)
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

# Initialize Pyrebase (for auth and user operations)
firebase = pyrebase.initialize_app(firebaseConfig)
pb_auth = firebase.auth()

# Initialize Firestore
use_firestore = True
db = firestore.client()

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