function getEnv(name: string): string {
  const value = process.env[name];

  if (!value) {
    throw new Error(`Missing environment variable: ${name}`);
  }

  return value;
}

export function getFirebaseConfig() {
  return {
    apiKey: getEnv("FIREBASE_API_KEY"),
    authDomain: getEnv("FIREBASE_AUTH_DOMAIN"),
    projectId: getEnv("FIREBASE_PROJECT_ID"),
    storageBucket: getEnv("FIREBASE_STORAGE_BUCKET"),
    messagingSenderId: getEnv("FIREBASE_MESSAGING_SENDER_ID"),
    appId: getEnv("FIREBASE_APP_ID"),
  };
}

export function getFirebaseAdminConfig() {
  return {
    projectId: getEnv("FIREBASE_PROJECT_ID"),
    clientEmail: getEnv("FIREBASE_CLIENT_EMAIL"),
    privateKey: getEnv("FIREBASE_PRIVATE_KEY").replaceAll(String.raw`\n`, "\n"),
  };
}
