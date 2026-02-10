import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";
import axios from "axios";
import { API_URL } from "../constants/api";
import type { User, CartItem, CartContextType, Props } from "../api/types";


const CartContext = createContext<CartContextType>({
  cart: [],
  addToCart: async () => {},
  fetchCart: async () => {},
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
            id: i.product_id,
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
        { product_id: item.id, quantity: item.quantity },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.items) {
        setCart(
          response.data.items.map((i: any) => ({
            id: i.product_id,
            name: i.product_name,
            price: Number(i.price),
            quantity: i.quantity,
          }))
        );
      } else {
        setCart((prev) => {
          const exist = prev.find((i) => i.id === item.id);
          if (exist) {
            return prev.map((i) =>
              i.id === item.id
                ? { ...i, quantity: i.quantity + item.quantity }
                : i
            );
          }
          return [...prev, item];
        });
      }
    } catch (err) {
      console.error("Error adding to cart:", err);
    }
  };

  return (
    <CartContext.Provider value={{ cart, addToCart, fetchCart }}>
      {children}
    </CartContext.Provider>
  );
};
