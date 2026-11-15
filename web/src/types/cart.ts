// Mirrors api/app/schemas/cart.py. Decimals arrive as strings.
export type CartLine = {
    id: number;
    variant_id: number;
    product_id: number;
    product_slug: string;
    name: string;
    sku: string;
    size: string | null;
    image_url: string | null;
    quantity: number;
    unit_price: string;
    unit_price_at_add: string | null;
    line_total: string;
    available: number;
};

export type Cart = {
    id: number | null;
    items: CartLine[];
    subtotal: string;
    currency: string;
};
