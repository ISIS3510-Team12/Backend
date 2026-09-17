# Firebase Auth Test CLI

Quickly create or sign in a Firebase user and print a Firebase ID token to test
the backend without using the mobile app.

## Setup

### Web app credentials

These values configure the Firebase client SDK. They come from your Firebase
Web app and go in `.env`.

1. In Firebase, enable **Authentication > Sign-in method > Email/Password**.
2. Open **Project settings > General > Your apps**.
3. Select or create a Web app (`</>`), then select **Config**.
4. Copy its values into `tools/firebase-auth/.env`:

```dotenv
FIREBASE_CREDENTIAL_PATH=./firebase_credential.json
FIREBASE_API_KEY=your-api-key
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-storage-bucket
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id
```

The Web API key is the `apiKey` value in that Firebase config.

### Admin credentials

This credential configures the Firebase Admin SDK. It is a private
service-account JSON file and does not go in `.env`.

1. Open **Project settings > Service accounts > Generate new private key**.
2. Save the downloaded file here as `firebase_credential.json`.

## Run

From the backend repository root:

```powershell
cd tools/firebase-auth
pnpm install
pnpm test:firebase-auth
```

Choose **Sign up** to create a test user or **Sign in** to get a token for an
existing user. The CLI prints the user's Firebase ID token and verifies it
with Firebase Admin.
