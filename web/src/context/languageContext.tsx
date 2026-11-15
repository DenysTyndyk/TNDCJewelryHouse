import React, { createContext, useContext, useState, useEffect } from 'react';
import translations from '../i18n/translations.json';

export type Language = 'uk' | 'pl' | 'en';

const LANGUAGES: Language[] = ['uk', 'pl', 'en'];
const DEFAULT_LANGUAGE: Language = 'uk';

type LanguageContextValue = {
  language: Language;
  setLanguage: (lang: Language) => void;
  languages: Language[];
  t: (key: string) => string;
};

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

function resolve(lang: Language, key: string): string | undefined {
  const parts = key.split('.');
  let node: any = (translations as any)[lang];
  for (const part of parts) {
    if (node == null) return undefined;
    node = node[part];
  }
  return typeof node === 'string' ? node : undefined;
}

export const LanguageProvider = ({ children }: { children: React.ReactNode }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    try {
      const saved = localStorage.getItem('language');
      return saved && LANGUAGES.includes(saved as Language) ? (saved as Language) : DEFAULT_LANGUAGE;
    } catch {
      return DEFAULT_LANGUAGE;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('language', language);
    } catch {
      // ignore storage errors (e.g. private browsing)
    }
  }, [language]);

  const setLanguage = (lang: Language) => setLanguageState(lang);

  const t = (key: string) => resolve(language, key) ?? resolve(DEFAULT_LANGUAGE, key) ?? key;

  return (
    <LanguageContext.Provider value={{ language, setLanguage, languages: LANGUAGES, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return ctx;
};
