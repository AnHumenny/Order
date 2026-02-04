import axios from "axios";
import type { Category } from "../api/types";
import { API_URL } from '../constants/api';

export const getCategories = async (): Promise<Category[]> => {
  const response = await axios.get(`${API_URL}/categories/`);
  return response.data;
};
