import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const getProducts = async () => {
  const res = await axios.get(`${API_URL}/products/`);
  return res.data;
};

export const getProductById = async (id: number) => {
  const res = await axios.get(`${API_URL}/products/${id}`);
  return res.data;
};
