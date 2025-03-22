# Environment Variables Setup

This application uses environment variables to store sensitive configuration information. This improves security by preventing sensitive credentials from being committed to version control.

## Setting Up Your .env File

1. Copy the `.env` file template to a new file named `.env`:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and fill in your actual values:

### Database Configuration
- `DB_PATH`: Path to the SQLite database file (default: "hot100.db")

### Firebase Client Configuration
Get these values from your Firebase project settings (Project Settings > General):
- `FIREBASE_API_KEY`: Your Firebase Web API Key
- `FIREBASE_AUTH_DOMAIN`: Your Firebase Auth Domain
- `FIREBASE_DATABASE_URL`: Your Firebase Database URL
- `FIREBASE_PROJECT_ID`: Your Firebase Project ID
- `FIREBASE_STORAGE_BUCKET`: Your Firebase Storage Bucket
- `FIREBASE_MESSAGING_SENDER_ID`: Your Firebase Messaging Sender ID
- `FIREBASE_APP_ID`: Your Firebase App ID

### Firebase Admin SDK (Service Account)
Get these values from your Firebase project service account (Project Settings > Service Accounts > Generate New Private Key):
- `FIREBASE_PRIVATE_KEY_ID`: Private Key ID from your service account JSON
- `FIREBASE_PRIVATE_KEY`: The full private key including the BEGIN and END markers
- `FIREBASE_CLIENT_EMAIL`: Client email from your service account
- `FIREBASE_CLIENT_ID`: Client ID from your service account
- `FIREBASE_CLIENT_CERT_URL`: Client certificate URL from your service account

### YouTube API Configuration (Optional)
- `YOUTUBE_API_KEY`: Your YouTube API Key (if you want to use the YouTube API)

### Application Settings
- `DEFAULT_UPDATE_INTERVAL`: How often metadata should be updated in seconds (default: 604800, which is 7 days)

## Important Notes

- **Never commit your `.env` file to version control!** It's already included in the `.gitignore` file.
- Keep your API keys and credentials secure.
- If your private key contains newlines, use the format: `FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour Private Key Here\n-----END PRIVATE KEY-----\n"` (the newlines will be properly handled by the code)

## Converting Firebase Service Account JSON to .env Format

If you download a Firebase service account JSON file, you can convert it to the required .env format with these steps:

1. Open the JSON file
2. For each key in the JSON, create a corresponding entry in your .env file:
   - `project_id` → `FIREBASE_PROJECT_ID`
   - `private_key_id` → `FIREBASE_PRIVATE_KEY_ID`
   - `private_key` → `FIREBASE_PRIVATE_KEY` (ensure the newlines are preserved with \n)
   - `client_email` → `FIREBASE_CLIENT_EMAIL`
   - `client_id` → `FIREBASE_CLIENT_ID`
   - `client_x509_cert_url` → `FIREBASE_CLIENT_CERT_URL` 