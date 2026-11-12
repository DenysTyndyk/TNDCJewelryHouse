import type { Item } from './item';
export type CartContextValue = {
    cartItems: Item[];
    cartCount: number;
    isInCart: (id: number) => boolean;
    toggleCart: (product: Item) => void;
    addToCart: (product: Item) => void;
    setQuantity: (id: number, quantity: number) => void;
  };