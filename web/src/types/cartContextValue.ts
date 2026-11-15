import type { Cart } from './cart';
export type CartContextValue = {
    cart: Cart;
    cartCount: number;
    error: string | null;
    isInCart: (variantId: number) => boolean;
    addToCart: (variantId: number, quantity?: number) => Promise<void>;
    setQuantity: (lineId: number, quantity: number) => Promise<void>;
    removeFromCart: (lineId: number) => Promise<void>;
    refresh: () => Promise<void>;
  };
