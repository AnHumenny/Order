import axios from "axios";
import { API_URL } from "../constants/api";

export const addProductToCart = async (productId: number) => {
  try {
    const response = await axios.post(`${API_URL}/cart/items`, {
      product_id: productId,
    });
    return response.data;
  } catch (error) {
    console.error("Failed to add product to cart:", error);
    throw error;
  }
};
