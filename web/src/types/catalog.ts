export type Locale = 'uk' | 'pl' | 'en';
export type SortOrder = 'newest' | 'price_asc' | 'price_desc' | 'popular';
export type Currency = 'UAH' | 'PLN' | 'USD';
export type MetalType = 'Gold' | 'Silver' | 'Platinum';
export type MetalColor = 'White' | 'Yellow' | 'Rose' | 'Bicolor';

export interface ProductImage {
  id: number;
  url: string;
  srcset: string | null;
  alt_text: string | null;
  width: number | null;
  height: number | null;
  is_primary: boolean;
  variant_id: number | null;
}

export interface ProductVariant {
  id: number;
  sku: string;
  size: string | null;
  length_mm: number | null;
  weight: string | null;
  metal_type: MetalType | null;
  metal_color: MetalColor | null;
  fineness: number | null;
  price: string;
  sale_price: string | null;
  currency: Currency;
  in_stock: boolean;
}

export interface CategoryNode {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  children: CategoryNode[];
}

export interface ProductListItem {
  id: number;
  slug: string;
  name: string;
  category_slug: string;
  price_from: string;
  currency: Currency;
  has_sale: boolean;
  in_stock: boolean;
  is_featured: boolean;
  image: ProductImage | null;
}

export interface ProductGemstone {
  slug: string;
  name: string;
  gemstone_type: 'Natural' | 'LabGrown';
  quantity: number;
  carat: string | null;
  cut_type: string | null;
  color_grade: string | null;
  clarity_grade: string | null;
  is_center_stone: boolean;
  variant_id: number | null;
}


export interface ProductDetail {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  meta_title: string | null;
  meta_description: string | null;
  category: CategoryNode;
  variants: ProductVariant[];
  images: ProductImage[];
  gemstones: ProductGemstone[];
}

export interface ProductPage {
  items: ProductListItem[];
  next_cursor: string | null;
}

export interface ProductFilters {
  category?: string;
  metal?: MetalType;
  color?: MetalColor;
  fineness?: number;
  price_min?: number;
  price_max?: number;
  gemstone?: string;
  in_stock?: boolean;
  sort?: SortOrder;
  cursor?: string;
  limit?: number;
  locale?: Locale;
}