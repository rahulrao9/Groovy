import os
import json
import subprocess
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def update_firebase_config():
    """Check if Firebase config from environment variables is set up correctly."""
    required_env_vars = [
        "FIREBASE_API_KEY", 
        "FIREBASE_AUTH_DOMAIN", 
        "FIREBASE_DATABASE_URL", 
        "FIREBASE_PROJECT_ID", 
        "FIREBASE_STORAGE_BUCKET", 
        "FIREBASE_MESSAGING_SENDER_ID", 
        "FIREBASE_APP_ID",
        # Also check for the service account variables
        "FIREBASE_PRIVATE_KEY_ID",
        "FIREBASE_PRIVATE_KEY",
        "FIREBASE_CLIENT_EMAIL",
        "FIREBASE_CLIENT_ID",
        "FIREBASE_CLIENT_CERT_URL"
    ]
    
    # Check if all required environment variables are set
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("\n⚠️  WARNING: Missing required Firebase configuration environment variables: ⚠️")
        for var in missing_vars:
            print(f"- {var}")
        print("\nPlease add these variables to your .env file")
        print("See ENV_SETUP.md for instructions on setting up environment variables\n")
    
    # Check if Firebase credentials are valid
    try:
        import firebase_config as fb
        # Try to access a collection to see if Firestore exists
        fb.get_firestore_db().collection('test').get()
    except Exception as e:
        if "The database (default) does not exist" in str(e):
            print("\n⚠️  WARNING: Firestore database not found! ⚠️")
            print("You need to create a Firestore database in your Firebase project:")
            print("1. Go to Firebase console: https://console.firebase.google.com/")
            print("2. Navigate to your project")
            print("3. Click on 'Firestore Database' in the left menu")
            print("4. Click 'Create database'")
            print("5. Select a location close to your users")
            print("6. Start in test mode for development, then set up security rules later\n")
        else:
            print(f"\n⚠️  WARNING: Firebase configuration error: {e} ⚠️")
            print("Please check your .env file and make sure all Firebase credentials are correct\n")

def create_groovy_logo():
    """Create a placeholder logo if it doesn't exist."""
    if not os.path.exists("assets/groovy_logo.png"):
        # Check if default.jpg exists and copy it
        if os.path.exists("assets/default.jpg"):
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            
            # Create a simple logo
            img = Image.new('RGB', (400, 400), color = (255, 255, 255))
            d = ImageDraw.Draw(img)
            
            # Add gradients or simple designs
            for i in range(400):
                for j in range(400):
                    # Create a radial gradient
                    distance = np.sqrt((i-200)**2 + (j-200)**2)
                    # Mix orange and pink
                    if distance < 180:
                        # Gradient from orange to pink
                        ratio = distance / 180
                        r = int(255 * (1 - ratio) + 229 * ratio)
                        g = int(138 * (1 - ratio) + 46 * ratio)
                        b = int(0 * (1 - ratio) + 113 * ratio)
                        img.putpixel((i, j), (r, g, b))
            
            # Add text "Groovy"
            try:
                d.text((150, 180), "Groovy", fill=(255, 255, 255))
            except:
                print("Could not add text to logo")
            
            img.save('assets/groovy_logo.png')
            print("Created placeholder logo")
        else:
            print("Could not create logo - assets/default.jpg not found")

def main():
    """Main function to prepare and launch Groovy app."""
    print("Preparing to launch Groovy...")
    
    # Make sure necessary directories exist
    os.makedirs("assets", exist_ok=True)
    os.makedirs("assets/music", exist_ok=True)
    os.makedirs("assets/meta", exist_ok=True)
    os.makedirs("assets/imgs", exist_ok=True)
    
    # Create placeholder logo
    create_groovy_logo()
    
    # Check Firebase config
    try:
        update_firebase_config()
    except Exception as e:
        print(f"Error checking Firebase config: {e}")
    
    # Launch the Streamlit app
    print("Launching Groovy app...")
    subprocess.run(["streamlit", "run", "Groovy.py"])

if __name__ == "__main__":
    main() 