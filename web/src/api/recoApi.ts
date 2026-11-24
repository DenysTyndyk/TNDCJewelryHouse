import { ownerRequest } from './cartApi';
import { request } from './authApi';
import { toQuery } from './catalogApi';
import { TRACKING_HEADER } from './telemetryApi';
import type { Locale, ProductFilters, ProductListItem, ProductPage } from '../types';

export type RecoAlgorithm = 'content' | 'vector' | 'popularity' | 'hybrid' | 'history' | 'co_view';
export type RecoResponse = { algorithm: RecoAlgorithm; items: ProductListItem[] };
export type Suggestion = { slug: string; name: string };

// ownerRequest: the backend needs the user/session to personalise; the header only says consent was given.
export function getRecommendations(
  path: string,
  params: Record<string, unknown>,
  accessToken: string | null,
  consented: boolean,
): Promise<RecoResponse> {
  return ownerRequest(
    `/recommendations/${path}${toQuery(params)}`,
    accessToken,
    consented ? { headers: { [TRACKING_HEADER]: 'granted' } } : {},
  );
}

// Catalog page in the personal order (sort=recommended): same /products, but sent with the owner and consent.
export function listRecommendedProducts(
  filters: ProductFilters,
  accessToken: string | null,
  consented: boolean,
): Promise<ProductPage> {
  return ownerRequest(
    `/products${toQuery({ ...filters, sort: 'recommended' })}`,
    accessToken,
    consented ? { headers: { [TRACKING_HEADER]: 'granted' } } : {},
  );
}

export function suggestProducts(q: string, locale: Locale, signal: AbortSignal): Promise<Suggestion[]> {
  return request(`/search/suggest${toQuery({ q, locale })}`, { signal });
}
