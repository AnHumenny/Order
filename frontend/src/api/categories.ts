import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export type Category = {
  id: number;
  name: string;
};

export const getCategories = async (): Promise<Category[]> => {
  const response = await axios.get(`${API_URL}/categories/`);
  return response.data;
};
