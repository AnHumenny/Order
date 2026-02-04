import axios from "axios";
import type { Product } from "./types";
import { API_URL } from '../constants/api';

export const getProductsByCategory = async (
  categoryId: number
): Promise<Product[]> => {
  try {
    const response = await axios.get(
      `${API_URL}/products/categories/${categoryId}/products`
    );
    return response.data;
  } catch (error) {
    console.error("Failed to fetch products by category:", error);
    return [];
  }
};
