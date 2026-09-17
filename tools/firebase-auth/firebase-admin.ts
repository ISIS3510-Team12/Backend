import { cert, initializeApp } from "firebase-admin/app";
import {
  getAuth,
  type DecodedIdToken,
} from "firebase-admin/auth";

import { getFirebaseAdminConfig } from "./config.js";

const adminAuth = getAuth(
  initializeApp({
    credential: cert(getFirebaseAdminConfig()),
  }),
);

export function verifyFirebaseIdToken(
  idToken: string,
): Promise<DecodedIdToken> {
  return adminAuth.verifyIdToken(idToken);
}
