import { request } from './authApi';
import { toQuery } from './catalogApi';
import type { Cart, Locale } from '../types';

const SESSION_HEADER = 'X-Cart-Session';
const SESSION_KEY = 'cartSession';

function readSession(): string | null {
    try { return localStorage.getItem(SESSION_KEY); } catch { return null; }
}

function saveSession(res: Response) {
    const token = res.headers.get(SESSION_HEADER);
    if (!token) return;
    try { localStorage.setItem(SESSION_KEY, token); } catch { /* ignore */ }
}

export function getCartSession(): string | null {
    return readSession();
}

export function clearCartSession() {
    try { localStorage.removeItem(SESSION_KEY); } catch { /* ignore */ }
}

// Logged-in users are identified by the bearer token; guests by X-Cart-Session (cart, orders, events).
export function ownerRequest(path: string, accessToken: string | null, options: RequestInit = {}) {
    const headers: Record<string, string> = { ...(options.headers as Record<string, string> | undefined) };
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
    const session = readSession();
    if (session) headers[SESSION_HEADER] = session;
    return request(path, { ...options, headers }, saveSession);
}

function cartRequest(path: string, accessToken: string | null, locale?: Locale, options: RequestInit = {}): Promise<Cart> {
    return ownerRequest(`/cart${path}${toQuery({ locale })}`, accessToken, options);
}

export function getCart(accessToken: string | null, locale?: Locale) {
    return cartRequest('', accessToken, locale);
}

export function addCartItem(variantId: number, quantity: number, accessToken: string | null, locale?: Locale) {
    return cartRequest('/items', accessToken, locale, {
        method: 'POST',
        body: JSON.stringify({ variant_id: variantId, quantity }),
    });
}

export function updateCartItem(itemId: number, quantity: number, accessToken: string | null, locale?: Locale) {
    return cartRequest(`/items/${itemId}`, accessToken, locale, {
        method: 'PATCH',
        body: JSON.stringify({ quantity }),
    });
}

export function removeCartItem(itemId: number, accessToken: string | null, locale?: Locale) {
    return cartRequest(`/items/${itemId}`, accessToken, locale, { method: 'DELETE' });
}
