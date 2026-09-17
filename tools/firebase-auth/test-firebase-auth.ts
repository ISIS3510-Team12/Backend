import * as prompts from "@clack/prompts";
import colors from "picocolors";

import { verifyFirebaseIdToken } from "./firebase-admin.js";
import { signIn, signUp } from "./firebase-auth.js";

type AuthAction = "sign-in" | "sign-up";

interface Credentials {
  email: string;
  password: string;
}

async function promptForAction(): Promise<AuthAction | null> {
  const action = await prompts.select({
    message: "Choose an authentication action",
    options: [
      {
        value: "sign-in" as const,
        label: "Sign in",
        hint: "Get a token for an existing user",
      },
      {
        value: "sign-up" as const,
        label: "Sign up",
        hint: "Create a new Firebase user",
      },
    ],
  });

  if (prompts.isCancel(action)) {
    prompts.cancel("Authentication cancelled");
    return null;
  }

  return action;
}

async function promptForCredentials(): Promise<Credentials | null> {
  const email = await prompts.text({
    message: "Email",
    placeholder: "user@example.com",
    validate(value) {
      if (!value?.trim()) {
        return "Email is required";
      }
    },
  });

  if (prompts.isCancel(email)) {
    prompts.cancel("Authentication cancelled");
    return null;
  }

  const password = await prompts.password({
    message: "Password",
    mask: "*",
    validate(value) {
      if (!value) {
        return "Password is required";
      }
    },
  });

  if (prompts.isCancel(password)) {
    prompts.cancel("Authentication cancelled");
    return null;
  }

  return {
    email: email.trim(),
    password,
  };
}

function formatError(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "Unknown authentication error";
}

prompts.intro(
  colors.bgRed(colors.white(colors.bold(" FIREBASE AUTH "))),
);

const action = await promptForAction();

if (action) {
  const credentials = await promptForCredentials();

  if (credentials) {
    const spinner = prompts.spinner();
    spinner.start(
      action === "sign-in" ? "Signing in" : "Creating account",
    );

    try {
      const authenticate = action === "sign-in" ? signIn : signUp;
      const { user } = await authenticate(
        credentials.email,
        credentials.password,
      );
      const idToken = await user.getIdToken(true);
      const claims = await verifyFirebaseIdToken(idToken);

      spinner.stop("Authentication successful");

      prompts.log.success(
        `${colors.bold("User:")} ${user.email ?? "No email"}`,
      );
      prompts.log.info(`${colors.bold("UID:")} ${user.uid}`);
      prompts.log.message(
        `${colors.bold(colors.yellow("Firebase ID token"))}\n${colors.dim(idToken)}`,
      );
      prompts.log.info(
        `${colors.bold("Expires:")} ${new Date(
          claims.exp * 1_000,
        ).toLocaleString()}`,
      );

      prompts.outro(colors.green("Firebase authentication complete"));
    } catch (error: unknown) {
      spinner.stop("Authentication failed");
      prompts.log.error(formatError(error));
      prompts.outro(colors.red("Firebase authentication failed"));
      process.exitCode = 1;
    }
  }
}
