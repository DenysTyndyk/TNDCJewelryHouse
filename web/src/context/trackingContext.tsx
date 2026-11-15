import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { sendEvents, type TrackEvent } from '../api/telemetryApi';
import { useAuth } from './authContext';

export type Consent = 'granted' | 'denied' | null; // null = not decided yet → show the banner

type TrackingContextValue = {
  consent: Consent;
  ready: boolean;
  canTrack: boolean;
  setConsent: (value: 'granted' | 'denied') => Promise<void>;
  track: (event: TrackEvent) => void;
};

const CONSENT_KEY = 'trackingConsent';
const FLUSH_INTERVAL_MS = 10_000;
const FLUSH_AT = 20;
const MAX_BATCH = 50; // server limit

function readGuestConsent(): Consent {
  try {
    const v = localStorage.getItem(CONSENT_KEY);
    return v === 'granted' || v === 'denied' ? v : null;
  } catch {
    return null;
  }
}

const TrackingContext = createContext<TrackingContextValue | undefined>(undefined);

// shortcut: events still queued at sign-out are sent as guest events; flush before signOut if that matters.
export const TrackingProvider = ({ children }: { children: React.ReactNode }) => {
  const { user, accessToken, loading, setAnalyticsConsent } = useAuth();
  const [guestConsent, setGuestConsent] = useState<Consent>(readGuestConsent);

  // Logged in: only the account's own decision counts. An account that never decided
  // (no consent_updated_at) gets the banner again; a withdrawal on another device is respected.
  const consent: Consent = user
    ? user.consent_updated_at ? (user.consent_analytics ? 'granted' : 'denied') : null
    : guestConsent;
  const canTrack = !loading && consent === 'granted';

  const queue = useRef<TrackEvent[]>([]);
  const tokenRef = useRef(accessToken);
  tokenRef.current = accessToken; // the interval below must always use the current token

  const flush = useCallback((keepalive = false) => {
    if (queue.current.length === 0) return;
    const batch = queue.current.splice(0, MAX_BATCH);
    sendEvents(batch, tokenRef.current, keepalive).catch(() => { /* telemetry is best effort */ });
  }, []);

  // Withdrawal (or logout into an undecided state) drops anything not yet sent.
  useEffect(() => {
    if (!canTrack) queue.current = [];
  }, [canTrack]);

  useEffect(() => {
    const timer = setInterval(() => flush(), FLUSH_INTERVAL_MS);
    // visibilitychange is the reliable "user left" signal on mobile; pagehide covers desktop close.
    const onHidden = () => { if (document.visibilityState === 'hidden') flush(true); };
    const onPageHide = () => flush(true);
    document.addEventListener('visibilitychange', onHidden);
    window.addEventListener('pagehide', onPageHide);
    return () => {
      clearInterval(timer);
      document.removeEventListener('visibilitychange', onHidden);
      window.removeEventListener('pagehide', onPageHide);
    };
  }, [flush]);

  const track = useCallback((event: TrackEvent) => {
    if (!canTrack) return; // no consent → nothing is queued, not even in memory
    queue.current.push(event);
    if (queue.current.length >= FLUSH_AT) flush();
  }, [canTrack, flush]);

  async function setConsent(value: 'granted' | 'denied') {
    if (user) {
      await setAnalyticsConsent(value === 'granted');
      return;
    }
    try { localStorage.setItem(CONSENT_KEY, value); } catch { /* private mode: keep it for this tab */ }
    setGuestConsent(value);
  }

  return (
    <TrackingContext.Provider value={{ consent, ready: !loading, canTrack, setConsent, track }}>
      {children}
    </TrackingContext.Provider>
  );
};

export const useTracking = () => {
  const ctx = useContext(TrackingContext);
  if (!ctx) throw new Error('useTracking must be used within TrackingProvider');
  return ctx;
};
