import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useLogout } from "../hooks/useLogout";
import "../styles/auth/AuthUser.css";

const UserBox: React.FC = () => {
  const { user } = useAuth();
  const { cart } = useCart();
  const logout = useLogout();

  if (!user) {
    return (
      <div className="user-box">
        <Link to="/login" className="login-link">
          Авторизация
        </Link>
      </div>
    );
  }

  return (
    <div className="user-box">

      <Link to="/" className="profile-link">
        Главная
      </Link>

      <span style={{ margin: "0 6px" }}>|</span>

      <Link to="/cart" className="profile-link">
        Корзина ({cart.length})
      </Link>

      <span style={{ margin: "0 6px" }}>|</span>

      <Link to="/me" className="profile-link">
        Кабинет
      </Link>

      <span style={{ margin: "0 8px" }}>|</span>
      <span>Hi, {user.username}</span>

      <button onClick={logout}>Logout</button>
    </div>
  );
};

export default UserBox;
