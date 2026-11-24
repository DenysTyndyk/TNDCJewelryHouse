import { ownerRequest } from './cartApi';

export const TRACKING_HEADER = 'X-Tracking-Consent';

// Only the types a client may send; Purchase is recorded by the backend at checkout.
export type EventType =
  | 'ProductView' | 'CategoryView' | 'AddToCart' | 'RemoveFromCart' | 'FilterApply' | 'Search';

export type TrackEvent = {
  event_type: EventType;
  product_id?: number;
  variant_id?: number;
  category_id?: number;
  metadata?: Record<string, string | number | boolean | null>;
};

// Events are only ever queued after consent, so the header is always "granted" here.
// keepalive lets the request finish while the tab is closing (sendBeacon cannot send headers).
export function sendEvents(events: TrackEvent[], accessToken: string | null, keepalive = false) {
  return ownerRequest('/events', accessToken, {
    method: 'POST',
    body: JSON.stringify({ events }),
    headers: { [TRACKING_HEADER]: 'granted' },
    keepalive,
  });
}
