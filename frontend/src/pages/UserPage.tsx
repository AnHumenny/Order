import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import CategoriesMenu from "../components/CategoriesMenu";
import { getCurrentUser } from "../api/user";
import { useLogout } from "../hooks/useLogout";
import "../styles/user/UserPage.css";
import "../styles/categories/CategoriesMenu.css";

interface User {
  id: number;
  username: string;
  email: string;
}

const UserPage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const logout = useLogout();

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch((err) => console.error("User load error:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!user)
    return (
      <div className="home-container">
        <div className="top-bar">
          <Link to="/login" className="login-link">
            Авторизация
          </Link>
        </div>
        <div>User not found</div>
      </div>
    );

  return (
    <div className="page-layout">

        <div className="user-box">
          <span>Hi, {user.username}</span>
          <button onClick={logout}>Logout</button>
        </div>

      <aside className="sidebar">
        <CategoriesMenu />
      </aside>

      <main className="page-content">
        <h3 className="page-title">Личный кабинет</h3>

        <div className="user-card">
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
