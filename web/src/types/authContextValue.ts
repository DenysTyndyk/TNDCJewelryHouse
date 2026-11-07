export type User = {
  id: number;
  email: string;
  role: string;
  status: string;
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
};
