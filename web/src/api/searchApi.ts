import { ownerRequest } from './cartApi';
import { toQuery } from './catalogApi';
import { TRACKING_HEADER } from './telemetryApi';
import type { ProductFilters, SearchMode, SearchResponse } from '../types';

// Order comes from the search ranking, so catalog sort/cursor do not apply here.
export type SearchParams = Omit<ProductFilters, 'sort' | 'cursor'> & {
  q: string;
  mode?: SearchMode;
  offset?: number;
};

// The consent header only lets the backend attach the session/user to the logged query (RODO).
export function searchProducts(params: SearchParams, accessToken: string | null, consented: boolean): Promise<SearchResponse> {
  return ownerRequest(
    `/search${toQuery(params)}`,
    accessToken,
    consented ? { headers: { [TRACKING_HEADER]: 'granted' } } : {},
  );
}
