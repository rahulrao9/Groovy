# Environment Variables Setup for Groovy

This guide will help you set up the necessary environment variables for the Groovy app, particularly focusing on Firebase authentication and configuration.

## Firebase Setup

### 1. Create a Firebase Project
1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" and follow the setup instructions
3. Enable Google Analytics if desired (optional)

### 2. Set Up Authentication
1. In the Firebase Console, navigate to your project
2. Go to "Authentication" in the left sidebar
3. Click "Get Started"
4. Enable the "Email/Password" sign-in method
5. Save the changes

### 3. Create a Firestore Database
1. In the Firebase Console, navigate to "Firestore Database"
2. Click "Create database"
3. Start in test mode (you can adjust security rules later)
4. Choose a database location that's closest to your users
5. Click "Enable"

### 4. Generate Firebase Web Config
1. In the Firebase Console, navigate to Project Settings (gear icon)
2. Under "General" tab, scroll down to "Your apps"
3. If you haven't already, click the web icon (</>) to add a web app
4. Register the app with a nickname (e.g., "Groovy Web")
5. Copy the Firebase configuration object that looks like this:
```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "your-project-id.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project-id.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID",
  measurementId: "YOUR_MEASUREMENT_ID"
};
```

### 5. Generate Service Account Key
1. In the Firebase Console, navigate to Project Settings
2. Go to the "Service accounts" tab
3. Click "Generate new private key"
4. Save the JSON file securely

## Setting Up .env File

1. Copy the `.env.example` file to create a new `.env` file:
```bash
cp .env.example .env
```

2. Open the `.env` file and fill in the values:

```
# Database Configuration
DB_PATH=hot100.db

# Firebase Web Config (Client Side)
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_MEASUREMENT_ID=your_measurement_id

# Firebase Admin SDK (Service Account)
FIREBASE_PRIVATE_KEY_ID=private_key_id_from_service_account_json
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour_Private_Key_Here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=client_email_from_service_account_json
FIREBASE_CLIENT_ID=client_id_from_service_account_json
FIREBASE_CLIENT_X509_CERT_URL=client_x509_cert_url_from_service_account_json

# Additional Configuration
YOUTUBE_API_KEY=your_youtube_api_key_optional
DEFAULT_UPDATE_INTERVAL=604800
```

### Notes on .env Values

- **Firebase Web Config**: These values come from the Firebase config object you copied earlier.
- **Firebase Admin SDK**: These values come from the service account JSON file you downloaded.
  - For the `FIREBASE_PRIVATE_KEY`, make sure to:
    - Include the entire key including the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`
    - Keep the newline characters (`\n`)
    - Enclose the entire key in double quotes
- **Additional Configuration**:
  - `YOUTUBE_API_KEY` is optional but recommended for better YouTube search results
  - `DEFAULT_UPDATE_INTERVAL` is the time in seconds for metadata refresh (default: 7 days)

## Security Considerations

- Never commit your `.env` file to version control
- Ensure `.env` is included in your `.gitignore` file
- Keep your service account JSON file secure and do not share it

## Testing Your Configuration

After setting up your environment variables, you can test if they're being loaded correctly by running:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'Project ID: {os.getenv(\"FIREBASE_PROJECT_ID\")}')"
```

This should output your Firebase project ID if everything is set up correctly.

## Troubleshooting

- **"Invalid JWT Signature" error**: Double-check your `FIREBASE_PRIVATE_KEY` format in the `.env` file.
- **"Cannot find module 'firebase'" error**: Ensure you've installed all requirements with `pip install -r requirements.txt`.
- **Firestore connection issues**: Verify your project ID and ensure Firestore is enabled in your Firebase project.
- **Authentication failures**: Check that you've enabled Email/Password authentication in Firebase Console. 