import type { Locale } from './catalog';

export type User = {
  id: number;
  email: string;
  role: string;
  status: string;
  preferred_language: Locale;
  consent_analytics: boolean;
  consent_updated_at: string | null; // null = the account never decided on tracking
};

export type AuthResult = { error: string | null };

export type AuthContextValue = {
  user: User | null;
  accessToken: string | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<AuthResult>;
  signUp: (
    email: string,
    password: string,
    firstName?: string,
    lastName?: string,
    phoneNumber?: string
  ) => Promise<AuthResult>;
  signOut: () => Promise<void>;
  changeLanguage: (lang: Locale) => void;
  setAnalyticsConsent: (granted: boolean) => Promise<void>;
};
