import React, { createContext, useContext, useEffect, useState } from "react";
import * as authApi from "../api/authApi";
import type { AuthContextValue, AuthResult, Locale, User } from '../types';
import { useLanguage } from './languageContext';

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const { setLanguage } = useLanguage();

  // A signed-in user's saved language wins over the one in localStorage
  function applyUser(me: User) {
    setUser(me);
    setLanguage(me.preferred_language);
  }

  function changeLanguage(lang: Locale) {
    setLanguage(lang);
    if (!accessToken) return; // guests keep the choice in localStorage only
    authApi.updatePreferences(accessToken, lang)
      .then((me) => setUser(me))
      .catch(() => { /* the UI already switched; saving is best effort */ });
  }

  useEffect(() => {
    authApi.refresh().then(({ access_token }) => {
      setAccessToken(access_token);
      return authApi.me(access_token);
    }).then(applyUser).catch(() => {
      setAccessToken(null);
      setUser(null);
    })
    .finally(() => setLoading(false));
  }, []);

  async function signIn(email: string, password: string): Promise<AuthResult> {
    try {
      const { access_token } = await authApi.login(email, password);
      setAccessToken(access_token);
      applyUser(await authApi.me(access_token));
      return { error: null };
    }
    catch (err: any) {
      return { error: err.message };
    }
  }

  async function signUp(email: string, password: string, firstName?: string, lastName?: string, phoneNumber?: string): Promise<AuthResult> {
    try {
      await authApi.register(email, password, firstName, lastName, phoneNumber);
      return { error: null };
    }
    catch (err: any) {
      return { error: err.message };
    }
  }

  async function signOut() {
    try {
      await authApi.logout();
    } finally {
      setAccessToken(null);
      setUser(null);
    }
  }

  return (
    <AuthContext.Provider value={{ user, accessToken, loading, signIn, signUp, signOut, changeLanguage }}>
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
