import os
import json
import subprocess
import streamlit as st

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

def create_firebase_key():
    """Create a firebase-key.json file with placeholder data if it doesn't exist."""
    if not os.path.exists("firebase-key.json"):
        # Create a dummy file with instructions
        key_data = {
            "_INSTRUCTIONS": "Replace this file with your actual Firebase service account key",
            "type": "service_account",
            "project_id": "your-project-id",
            "private_key_id": "your-private-key-id",
            "private_key": "your-private-key",
            "client_email": "your-client-email",
            "client_id": "your-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "your-cert-url"
        }
        
        with open("firebase-key.json", "w") as f:
            json.dump(key_data, f, indent=2)
            
        print("Created placeholder firebase-key.json - replace with your actual Firebase service account key")
        print("\nHow to get your Firebase service account key:")
        print("1. Go to Firebase console: https://console.firebase.google.com/")
        print("2. Open your project")
        print("3. Click the gear icon (⚙️) next to 'Project Overview' and select 'Project settings'")
        print("4. Go to the 'Service accounts' tab")
        print("5. Click 'Generate new private key'")
        print("6. Save the downloaded file as 'firebase-key.json' in this directory")
        print("7. Make sure the file permissions are restricted (don't share this key!)\n")
    
def update_firebase_config():
    """Check if Firebase config has been updated."""
    import firebase_config as fb
    
    # Check if the API key is still the placeholder
    if fb.firebaseConfig["apiKey"] == "YOUR_API_KEY":
        print("\n⚠️  WARNING: Firebase configuration is not set up! ⚠️")
        print("Please update firebase_config.py with your Firebase project details.")
        print("Visit https://console.firebase.google.com/ to create a project and get your config.\n")
    
    # Check if all required keys are present
    required_keys = ["apiKey", "authDomain", "databaseURL", "projectId", "storageBucket", "messagingSenderId", "appId"]
    missing_keys = [key for key in required_keys if key not in fb.firebaseConfig]
    if missing_keys:
        print(f"\n⚠️  WARNING: Missing required Firebase configuration keys: {', '.join(missing_keys)} ⚠️")
        print("Please add these keys to your firebaseConfig dictionary in firebase_config.py")
        print("For the databaseURL, use: https://YOUR-PROJECT-ID.firebaseio.com\n")
        
    # Check if Firestore database needs to be created
    try:
        # Try to access a collection to see if Firestore exists
        fb.db.collection('test').get()
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
    
    # Create placeholder files
    create_firebase_key()
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