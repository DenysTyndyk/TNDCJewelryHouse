import React, { createContext, useContext, useState, useEffect } from "react";
import * as cartApi from '../api/cartApi';
import type { Cart, CartContextValue } from '../types';
import { useAuth } from './authContext';
import { useLanguage } from './languageContext';

const EMPTY_CART: Cart = { id: null, items: [], subtotal: '0.00', currency: 'UAH' };

const CartContext = createContext<CartContextValue | undefined>(undefined);

// The server owns the cart; only the guest session token lives in localStorage (see cartApi).
export const CartProvider = ({ children }: { children: React.ReactNode }) => {
  const { accessToken, loading: authLoading } = useAuth();
  const { language } = useLanguage();
  const [cart, setCart] = useState<Cart>(EMPTY_CART);
  const [error, setError] = useState<string | null>(null);

  // Reload when the owner (guest/user) or the content language changes.
  useEffect(() => {
    if (authLoading) return; // otherwise a guest cart is fetched before the refresh token resolves
    let active = true;
    cartApi.getCart(accessToken, language)
      .then((c) => { if (active) { setCart(c); setError(null); } })
      .catch((e: Error) => active && setError(e.message));
    return () => { active = false; };
  }, [accessToken, language, authLoading]);

  async function run(call: Promise<Cart>) {
    try {
      setCart(await call);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <CartContext.Provider
      value={{
        cart,
        cartCount: cart.items.reduce((sum, line) => sum + line.quantity, 0),
        error,
        isInCart: (variantId) => cart.items.some((line) => line.variant_id === variantId),
        addToCart: (variantId, quantity = 1) => run(cartApi.addCartItem(variantId, quantity, accessToken, language)),
        setQuantity: (lineId, quantity) => run(cartApi.updateCartItem(lineId, quantity, accessToken, language)),
        removeFromCart: (lineId) => run(cartApi.removeCartItem(lineId, accessToken, language)),
        refresh: () => run(cartApi.getCart(accessToken, language)),
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const ctx = useContext(CartContext);
  if (!ctx) {
    throw new Error('useCart must be used within CartProvider');
  }
  return ctx;
};
