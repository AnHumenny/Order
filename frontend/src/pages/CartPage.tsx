import React from "react";
import { Link } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useLogout } from "../hooks/useLogout";
import CategoriesMenu from "../components/CategoriesMenu";
import "../styles/products/ProductsGrid.css";
import "../styles/auth/AuthUser.css";
import "../styles/categories/CategoriesMenu.css";

const CartPage: React.FC = () => {
  const { cart } = useCart();
  const { user } = useAuth();
  const logout = useLogout();

  const total = cart.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  return (
    <div className="home-container">
      {!user && (
        <div className="user-box">
          <Link to="/login" className="login-link">
            Авторизация
          </Link>
        </div>
      )}

      {user && (
        <div className="user-box">
          <Link to="/" className="profile-link">
            Главная
          </Link>

          <div>
            <Link to="/me" className="profile-link">
              Кабинет
            </Link>
            <span style={{ margin: "0 8px" }}>|</span>
            <span>Hi, {user.username}</span>
          </div>

          <button onClick={logout}>Logout</button>
        </div>
      )}

      <div style={{ marginTop: "50px" }} />

      <div className="content-wrapper">
        <CategoriesMenu />

        <div className="product-page-content">
          <h3>Корзина</h3>

          {cart.length === 0 ? (
            <p>Ваша корзина пуста.</p>
          ) : (
            <>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th align="left">Товар</th>
                    <th align="center">Кол-во</th>
                    <th align="right">Цена</th>
                    <th align="right">Сумма</th>
                  </tr>
                </thead>
                <tbody>
                  {cart.map((item) => (
                    <tr key={item.id}>
                      <td>{item.name}</td>
                      <td align="center">{item.quantity}</td>
                      <td align="right">{item.price} €</td>
                      <td align="right">
                        {(item.price * item.quantity).toFixed(2)} €
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <hr />

              <h3 style={{ textAlign: "right" }}>
                Итого: {total.toFixed(2)} €
              </h3>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default CartPage;
