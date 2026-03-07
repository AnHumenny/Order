import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import axios from "axios";
import { API_URL } from "../constants/api";
import type { User, CartItem, CartContextType, Props } from "../api/types";

const CartContext = createContext<CartContextType>({
  cart: [],
  addToCart: async () => {},
  fetchCart: async () => {},
  clearCart: async () => {},
  updateQuantity: async () => {},
});

export const useCart = () => useContext(CartContext);

export const CartProvider: React.FC<Props> = ({ children }) => {
  const [cart, setCart] = useState<CartItem[]>([]);

  const getToken = () => localStorage.getItem("token");

  const fetchCart = async () => {
    try {
      const token = getToken();
      if (!token) return;

      const response = await axios.get(`${API_URL}/cart/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.data.items) {
        setCart(
          response.data.items.map((i: any) => ({
            id: i.id,
            product_id: i.product_id,
            name: i.product_name,
            price: Number(i.price),
            quantity: i.quantity,
          }))
        );
      }
    } catch (err) {
      console.error("Failed to fetch cart:", err);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const addToCart = async (item: CartItem) => {
    try {
      const token = getToken();
      if (!token) {
        console.error("User not authenticated");
        return;
      }

      const response = await axios.post(
        `${API_URL}/cart/items`,
        { product_id: item.product_id, quantity: item.quantity },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.items) {
        setCart(
          response.data.items.map((i: any) => ({
            id: i.id,
            product_id: i.product_id,
            name: i.product_name,
            price: Number(i.price),
            quantity: i.quantity,
          }))
        );
      } else {
        setCart((prev) => {
          const exist = prev.find((i) => i.product_id === item.product_id);
          if (exist) {
            return prev.map((i) =>
              i.product_id === item.product_id
                ? { ...i, quantity: i.quantity + item.quantity }
                : i
            );
          }
          return [...prev, { ...item, id: Date.now() }];
        });
      }
    } catch (err) {
      console.error("Error adding to cart:", err);
    }
  };

  const clearCart = async () => {
    try {
      const token = getToken();
      if (!token) {
        console.error("User not authenticated");
        return;
      }

      await axios.delete(`${API_URL}/cart/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setCart([]);

    } catch (err) {
      console.error("Error clearing cart:", err);
      throw err;
    }
  };

  const updateQuantity = async (productId: number, action: 'increment' | 'decrement') => {
    try {
      const token = getToken();
      if (!token) {
        console.error("User not authenticated");
        return;
      }

      const url = action === 'increment'
        ? `${API_URL}/cart/product/${productId}/increment`
        : `${API_URL}/cart/product/${productId}/decrement`;

      await axios.post(url, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setCart((prevCart) => {
        return prevCart.map((item) => {
          if (item.product_id === productId) {
            const newQuantity = action === 'increment'
              ? item.quantity + 1
              : item.quantity - 1;

            if (newQuantity <= 0) {
              return null;
            }

            return { ...item, quantity: newQuantity };
          }
          return item;
        }).filter(Boolean) as CartItem[];
      });

    } catch (err) {
      console.error(`Error ${action}ing item quantity:`, err);
      throw err;
    }
  };

  return (
    <CartContext.Provider value={{
      cart,
      addToCart,
      fetchCart,
      clearCart,
      updateQuantity
    }}>
      {children}
    </CartContext.Provider>
  );
};
