import React, { createContext, useContext, useState, useEffect } from "react";
import * as cartApi from '../api/cartApi';
import type { Cart, CartContextValue } from '../types';
import { useAuth } from './authContext';
import { useLanguage } from './languageContext';
import { useTracking } from './trackingContext';

const EMPTY_CART: Cart = { id: null, items: [], subtotal: '0.00', currency: 'UAH' };

const CartContext = createContext<CartContextValue | undefined>(undefined);

// The server owns the cart; only the guest session token lives in localStorage (see cartApi).
export const CartProvider = ({ children }: { children: React.ReactNode }) => {
  const { accessToken, loading: authLoading } = useAuth();
  const { language } = useLanguage();
  const { track } = useTracking();
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

  // Events only after the server confirmed the change (a 409 is not an "add to cart").
  async function addToCart(variantId: number, quantity = 1) {
    try {
      const next = await cartApi.addCartItem(variantId, quantity, accessToken, language);
      setCart(next);
      setError(null);
      const line = next.items.find((l) => l.variant_id === variantId);
      track({ event_type: 'AddToCart', variant_id: variantId, product_id: line?.product_id, metadata: { quantity } });
    } catch (e) {
      setError((e as Error).message);
    }
  }

  // shortcut: run() swallows errors, so a failed removal is still tracked; make run() return a boolean if it matters.
  async function removeFromCart(lineId: number) {
    const line = cart.items.find((l) => l.id === lineId); // read before the line disappears
    await run(cartApi.removeCartItem(lineId, accessToken, language));
    if (line) track({ event_type: 'RemoveFromCart', variant_id: line.variant_id, product_id: line.product_id });
  }

  return (
    <CartContext.Provider
      value={{
        cart,
        cartCount: cart.items.reduce((sum, line) => sum + line.quantity, 0),
        error,
        isInCart: (variantId) => cart.items.some((line) => line.variant_id === variantId),
        addToCart,
        setQuantity: (lineId, quantity) => run(cartApi.updateCartItem(lineId, quantity, accessToken, language)),
        removeFromCart,
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
