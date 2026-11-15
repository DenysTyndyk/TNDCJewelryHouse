// Mirrors api/app/schemas/order.py. Decimals arrive as strings.
export type DeliveryProvider = 'NovaPoshta' | 'UkrPoshta' | 'Courier';

export type OrderStatus = 'Pending' | 'Paid' | 'Processing' | 'Shipped' | 'Delivered' | 'Cancelled' | 'Returned';

export type ShippingMethod = {
    id: number;
    provider: DeliveryProvider;
    name: string;
    cost: string;
    currency: string;
    free_from_amount: string | null;
    delivery_days_min: number | null;
    delivery_days_max: number | null;
};

export type CheckoutForm = {
    recipient_name: string;
    recipient_phone: string;
    customer_email: string;
    shipping_method_id: number;
    shipping_city: string;
    provider_point_id: string | null;
    shipping_address_line: string | null;
    customer_note: string | null;
};

export type OrderItem = {
    variant_id: number | null;
    sku: string;
    product_name: string;
    quantity: number;
    unit_price: string;
    line_total: string;
};

export type Order = {
    order_number: string;
    status: OrderStatus;
    currency: string;
    subtotal: string;
    discount_amount: string;
    shipping_amount: string;
    total: string;
    shipping_method_id: number | null;
    recipient_name: string;
    recipient_phone: string;
    customer_email: string | null;
    shipping_city: string | null;
    shipping_address_line: string | null;
    provider_point_id: string | null;
    customer_note: string | null;
    tracking_number: string | null;
    created_at: string;
    paid_at: string | null;
    cancelled_at: string | null;
    items: OrderItem[];
};
