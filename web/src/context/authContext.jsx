import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

/**
 * Temporary auth stub. Milestone 2 replaces this with the FastAPI API
 * (`/auth/login`, `/auth/refresh`). Do not call Supabase from here.
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const loading = false;

  async function signIn() {
    return { error: "Auth API is not connected yet" };
  }

  async function signOut() {
    setSession(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, session, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};
