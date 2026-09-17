import { initializeApp } from "firebase/app";
import {
  createUserWithEmailAndPassword,
  getAuth,
  signInWithEmailAndPassword,
  type UserCredential,
} from "firebase/auth";

import { getFirebaseConfig } from "./config.js";

const auth = getAuth(
  initializeApp(getFirebaseConfig(), "firebase-auth-test"),
);

export function signUp(
  email: string,
  password: string,
): Promise<UserCredential> {
  return createUserWithEmailAndPassword(auth, email, password);
}

export function signIn(
  email: string,
  password: string,
): Promise<UserCredential> {
  return signInWithEmailAndPassword(auth, email, password);
}
