import { request } from './authApi';
import { ownerRequest } from './cartApi';
import { toQuery } from './catalogApi';
import type { CheckoutForm, Locale, Order, ShippingMethod } from '../types';

export function listShippingMethods(): Promise<ShippingMethod[]> {
    return request('/shipping-methods');
}

// locale picks the language of the product names snapshot and of the confirmation email.
export function createOrder(form: CheckoutForm, accessToken: string | null, locale?: Locale): Promise<Order> {
    return ownerRequest(`/orders${toQuery({ locale })}`, accessToken, {
        method: 'POST',
        body: JSON.stringify(form),
    });
}

export function listOrders(accessToken: string | null): Promise<Order[]> {
    return ownerRequest('/orders', accessToken);
}

export function getOrder(orderNumber: string, accessToken: string | null): Promise<Order> {
    return ownerRequest(`/orders/${encodeURIComponent(orderNumber)}`, accessToken);
}

export function cancelOrder(orderNumber: string, accessToken: string | null): Promise<Order> {
    return ownerRequest(`/orders/${encodeURIComponent(orderNumber)}/cancel`, accessToken, { method: 'POST' });
}
