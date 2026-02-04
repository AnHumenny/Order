import axios from "axios";
import { API_URL } from '../constants/api';

export const getCurrentUser = async () => {
  const token = localStorage.getItem("token");

  const response = await axios.get(`${API_URL}/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
};
