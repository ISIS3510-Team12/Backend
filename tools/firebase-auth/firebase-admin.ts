import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { cert, initializeApp } from "firebase-admin/app";
import {
  getAuth,
  type DecodedIdToken,
} from "firebase-admin/auth";

import { getFirebaseCredentialPath } from "./config.js";

interface FirebaseCredential {
  project_id: string;
  client_email: string;
  private_key: string;
}

function loadFirebaseCredential(): FirebaseCredential {
  const credentialPath = resolve(getFirebaseCredentialPath());
  const contents = readFileSync(credentialPath, "utf8");
  const credential = JSON.parse(contents) as Partial<FirebaseCredential>;

  if (
    !credential.project_id ||
    !credential.client_email ||
    !credential.private_key
  ) {
    throw new Error("Invalid Firebase Admin credential file");
  }

  return credential as FirebaseCredential;
}

const firebase_credential = loadFirebaseCredential();

const adminAuth = getAuth(
  initializeApp({
    credential: cert({
      projectId: firebase_credential.project_id,
      clientEmail: firebase_credential.client_email,
      privateKey: firebase_credential.private_key,
    }),
  }),
);

export function verifyFirebaseIdToken(
  idToken: string,
): Promise<DecodedIdToken> {
  return adminAuth.verifyIdToken(idToken);
}
