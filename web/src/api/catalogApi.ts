import { request } from './authApi';
import type { CategoryNode,Item, Locale, ProductDetail, ProductFilters, ProductListItem, ProductPage } from '../types';

export function toQuery(params: Record<string,unknown>): string{
    const qs = new URLSearchParams();
    for (const [key,value] of Object.entries(params)){
        if (value !== undefined && value !== null && value !=='') qs.append(key,String(value))
    }
    const s = qs.toString();
    return s ? `?${s}` : '';
}

export function toItem(p: ProductListItem): Item{
    return {
        id: p.id,
        slug: p.slug,
        title: p.name,
    price: Number(p.price_from),
    currency: p.currency,
    description: '',
    category: p.category_slug,
    images: p.image ? [p.image.url] : [],
  };
}

export function listCategories(locale?:Locale): Promise<CategoryNode[]>{
    return request(`/categories${toQuery({locale})}`);
}

export function listProducts(filters:ProductFilters={}): Promise<ProductPage>{
    return request(`/products${toQuery({...filters})}`);
}

export function getProductBySlug(slug: string, locale?: Locale): Promise<ProductDetail>{
    return request(`/products/${encodeURIComponent(slug)}${toQuery({locale})}`);
}