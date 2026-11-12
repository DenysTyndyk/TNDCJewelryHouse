import React, { createContext, useContext, useState, useEffect } from "react";
import type { Item, CartContextValue } from '../types';

const CartContext = createContext<CartContextValue | undefined>(undefined);

export const CartProvider = ({ children }: { children: React.ReactNode }) => {
  const [cartItems, setCartItems] = useState<Item[]>(() => {
    try {
      const saved = localStorage.getItem('cartItems');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    localStorage.setItem('cartItems', JSON.stringify(cartItems));
  }, [cartItems]);

  const isInCart = (id: number) => cartItems.some((item: Item) => item.id === id);

  const toggleCart = (product: Item) => {
    setCartItems((prevItems: Item[]) => {
      if (prevItems.some((item: Item) => item.id === product.id)) {
        return prevItems.filter((item: Item) => item.id !== product.id);
      } else {
        return [...prevItems, { ...product, quantity: 1 }];
      }
    });
  };

  const addToCart = (product: Item) => {
    setCartItems((prevItems: Item[]) =>
      prevItems.some((item) => item.id === product.id) ? prevItems : [...prevItems, { ...product, quantity: 1 }],
    );
  };

  const setQuantity = (id: number, quantity: number) => {
    setCartItems((prevItems: Item[]) =>
      quantity < 1
        ? prevItems.filter((item) => item.id !== id)
        : prevItems.map((item) => (item.id === id ? { ...item, quantity } : item)),
    );
  };

  return (
    <CartContext.Provider
      value={{
        cartItems,
        cartCount: cartItems.reduce((sum, item) => sum + (item.quantity ?? 1), 0),
        isInCart,
        toggleCart,
        addToCart,
        setQuantity,
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