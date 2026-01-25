import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export const useLogout = () => {
  const { logoutUser } = useAuth();
  const navigate = useNavigate();

  const logout = () => {
    logoutUser();
    navigate("/login");
  };

  return logout;
};
