import React from "react";
import { useAuth } from "../context/AuthContext";
import { useLogout } from "../hooks/useLogout";

const HomePage: React.FC = () => {
  const { user } = useAuth();
  const logout = useLogout();

  return (
    <div style={{ padding: 50 }}>
      <h3>Welcome {user?.username || "Guest"}!</h3>
      <p>You are successfully logged in.</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

export default HomePage;
