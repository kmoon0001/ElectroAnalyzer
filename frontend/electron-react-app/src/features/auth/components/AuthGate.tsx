import { ReactNode, useEffect, useState } from "react";

import { useAppStore } from "../../../store/useAppStore";
import { tokenManager } from "../../../lib/security/secureTokenStorage";
import { LoginOverlay } from "./LoginOverlay";

export const AuthGate = ({ children }: { children: ReactNode }) => {
  const token = useAppStore((state) => state.auth.token);
  const setCredentials = useAppStore((state) => state.auth.setCredentials);
  const [secureAuth, setSecureAuth] = useState<boolean>(false);

  useEffect(() => {
    // On mount, recover token from secure storage and hydrate store if present
    (async () => {
      const stored = await tokenManager.getAuthToken();
      if (stored && !token) {
        // Attempt to recover username (sub) from JWT payload
        let username = "";
        try {
          const payload = JSON.parse(atob(stored.split(".")[1]));
          username = payload?.sub || "";
        } catch {}
        await setCredentials({ username, token: stored });
        setSecureAuth(true);
      } else {
        setSecureAuth(Boolean(stored));
      }
    })().catch(() => setSecureAuth(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isAuthed = Boolean(token) || secureAuth;

  return (
    <>
      {children}
      {!isAuthed && <LoginOverlay />}
    </>
  );
};
