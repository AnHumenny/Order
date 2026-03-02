import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useLogout } from "../hooks/useLogout";
import CategoriesMenu from "../components/CategoriesMenu";
import UserBox from "../components/UserBox";
import "../styles/products/ProductsGrid.css";
import "../styles/auth/AuthUser.css";
import "../styles/categories/CategoriesMenu.css";
import "../styles/cart/CartPage.css";

const CartPage: React.FC = () => {
  const { cart, clearCart } = useCart();
  const { user } = useAuth();
  const logout = useLogout();
  const navigate = useNavigate();

  const [isClearing, setIsClearing] = useState<boolean>(false);

  const total: number = cart.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  const handleClearCart = async (): Promise<void> => {
    if (!window.confirm('Вы уверены, что хотите очистить корзину?')) {
      return;
    }

    setIsClearing(true);
    try {
      await clearCart();
      alert('Корзина успешно очищена!');
    } catch (error) {
      alert('Ошибка при очистке корзины. Попробуйте еще раз.');
    } finally {
      setIsClearing(false);
    }
  };

  const handleContinueShopping = (): void => {
    navigate('/');
  };

  const handleCheckout = (): void => {
    alert('Оформление заказа');
  };

  return (
    <div className="home-container">
      <UserBox user={user} cart={cart} onLogout={logout} />

      <div style={{ marginTop: "50px" }} />

      <div className="content-wrapper">
        <CategoriesMenu />

        <div className="product-page-content">
          <div className="cart-header">
            <h3>Корзина</h3>

            {cart.length > 0 && (
              <div className="cart-actions">
                <button
                  onClick={handleContinueShopping}
                  className="continue-shopping-btn"
                >
                  Продолжить покупки
                </button>
                <button
                  onClick={handleClearCart}
                  disabled={isClearing}
                  className="clear-cart-btn"
                >
                  {isClearing ? (
                    'Очистка...'
                  ) : (
                    <>
                      <span role="img" aria-label="trash">🗑️</span>
                      Очистить корзину
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {cart.length === 0 ? (
            <div className="empty-cart">
              <p>Ваша корзина пуста.</p>
              <button
                onClick={handleContinueShopping}
                className="go-to-shop-btn"
              >
                Перейти к покупкам
              </button>
            </div>
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
              {/* добавить +- item */}
                </tbody>
              </table>

              <hr />

              <div className="cart-total-section">
                <h3 className="cart-total">
                  Итого: {total.toFixed(2)} €
                </h3>
                <button
                  className="checkout-btn"
                  onClick={handleCheckout}
                >
                  Оформить заказ
                  {/* доработать checkout*/}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default CartPage;
