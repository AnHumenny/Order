import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import CategoriesMenu from "../components/CategoriesMenu";
import UserBox from "../components/UserBox";
import { getCurrentUser } from "../api/user";
import { useLogout } from "../hooks/useLogout";
import { useCart } from "../context/CartContext";
import "../styles/user/UserPage.css";
import "../styles/categories/CategoriesMenu.css";
import type { User } from "../api/types";


const UserPage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const logout = useLogout();
  const { cart } = useCart();

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch((err) => console.error("User load error:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;

  if (!user) {
    return (
      <div className="home-container">
        <UserBox user={null} cart={cart} onLogout={logout} />
        <div>User not found</div>
      </div>
    );
  }

  return (
    <div className="page-layout">
      <UserBox user={user} cart={cart} onLogout={logout} />

      <aside className="sidebar">
        <CategoriesMenu />
      </aside>

      <main className="page-content">

        <div className="user-card">
        <h3 className="page-title">Личный кабинет</h3>
        <p>------------------------------</p>
          <p>
            <strong>Имя пользователя:</strong> {user.username}
          </p>
          <p>
            <strong>Email:</strong> {user.email}
          </p>
        </div>
      </main>
    </div>
  );
};

export default UserPage;
