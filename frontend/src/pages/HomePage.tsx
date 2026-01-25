import React from "react";
import { useAuth } from "../context/AuthContext";
import { useLogout } from "../hooks/useLogout";
import "../styles/auth/AuthUser.css";

const HomePage: React.FC = () => {
  const { user } = useAuth();
  const logout = useLogout();

  return (
    <div className="user-box">
      <h4>Welcome {user?.username || "Guest"}!</h4>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

export default HomePage;
