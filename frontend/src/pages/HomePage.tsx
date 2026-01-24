import React from "react";
import { useAuth } from "../context/AuthContext";

const HomePage: React.FC = () => {
  const { user, logoutUser } = useAuth();

  return (
    <div style={{ padding: 50 }}>
      <h1>Welcome {user?.username || "Guest"}!</h1>
      <p>You are successfully logged in.</p>
      <button onClick={logoutUser}>Logout</button>
    </div>
  );
};

export default HomePage;
