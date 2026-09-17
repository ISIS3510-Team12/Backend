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
FIREBASE_API_KEY=your-api-key
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-storage-bucket
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

The Web API key is the `apiKey` value in that Firebase config.

### Admin credentials

These values configure the Firebase Admin SDK and come from a private
service-account key.

1. Open **Project settings > Service accounts > Generate new private key**.
2. Copy `client_email` to `FIREBASE_CLIENT_EMAIL`.
3. Copy `private_key` to `FIREBASE_PRIVATE_KEY`, keeping newline characters as
   `\n` in the `.env` value.

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
