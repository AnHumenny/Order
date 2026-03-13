import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useLogout } from "../hooks/useLogout";
import CategoriesMenu from "../components/CategoriesMenu";
import UserBox from "../components/UserBox";
import { API_URL, FRONTEND_URL } from "../constants/api";
import "../styles/products/ProductsGrid.css";
import "../styles/auth/AuthUser.css";
import "../styles/categories/CategoriesMenu.css";
import "../styles/cart/CartPage.css";
import type { OrderData, CheckoutSessionResponse } from "../api/types";


const CartPage: React.FC = () => {
  const { cart, clearCart, updateQuantity } = useCart();
  const { user } = useAuth();
  const logout = useLogout();
  const navigate = useNavigate();

  const [isClearing, setIsClearing] = useState<boolean>(false);
  const [isCheckingOut, setIsCheckingOut] = useState<boolean>(false);
  const [updatingItems, setUpdatingItems] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);

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

const handleCheckout = async (): Promise<void> => {
  setError(null);

  if (!user) {
    alert('Пожалуйста, войдите в систему для оформления заказа');
    navigate('/login');
    return;
  }

  if (cart.length === 0) {
    alert('Корзина пуста');
    return;
  }

  setIsCheckingOut(true);

  try {
    const orderData: OrderData = {
      items: cart.map(item => ({
        product_id: item.product_id,
        quantity: item.quantity,
        price: item.price
      })),
      total_amount: total
    };

    const token = localStorage.getItem('token') || localStorage.getItem('access_token');

    if (!token) {
      throw new Error('Токен авторизации не найден');
    }

    console.log('=== Оформление заказа ===');
    console.log('API_URL:', API_URL);
    console.log('Данные заказа:', orderData);
    console.log('Оформление заказа через /orders/checkout...');

    const checkoutResponse = await fetch(`${API_URL}/orders/checkout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
      },
      body: JSON.stringify(orderData)
    });

    if (!checkoutResponse.ok) {
      const errorData = await checkoutResponse.json().catch(() => null);
      console.error('Ошибка оформления заказа:', errorData);
      throw new Error(errorData?.detail || 'Ошибка при оформлении заказа');
    }

    const checkoutResult = await checkoutResponse.json();
    console.log('Заказ оформлен:', checkoutResult);
    console.log('Создание сессии Stripe...');

    const sessionData = {
      order_id: checkoutResult.id || checkoutResult.order_id,
      success_url: `http://localhost:5173/success`,
      cancel_url: `http://localhost:5173/cancel`,
    };

    const sessionResponse = await fetch(`${API_URL}/webhook/create-checkout-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
      },
      body: JSON.stringify(sessionData)
    });

    if (!sessionResponse.ok) {
      const errorData = await sessionResponse.json().catch(() => null);
      console.error('Ошибка создания сессии:', errorData);
      throw new Error(errorData?.detail || 'Ошибка при создании сессии оплаты');
    }

    const sessionResult = await sessionResponse.json();
    console.log('Сессия создана:', sessionResult);

    const checkoutUrl = sessionResult.url || sessionResult.checkout_url;

    if (checkoutUrl) {
      window.location.href = checkoutUrl;
    } else {
      throw new Error('Не удалось получить URL для оплаты');
    }

  } catch (error) {
    console.error('❌ Ошибка оформления заказа:', error);

    let errorMessage = 'Ошибка при оформлении заказа. ';

    if (error instanceof Error) {
      errorMessage += error.message;
    }

    setError(errorMessage);
    alert(errorMessage);
  } finally {
    setIsCheckingOut(false);
  }
  };


  const handleIncrement = async (productId: number): Promise<void> => {
    setUpdatingItems(prev => new Set(prev).add(productId));
    try {
      await updateQuantity(productId, 'increment');
    } catch (error) {
      alert('Ошибка при увеличении количества');
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(productId);
        return newSet;
      });
    }
  };

  const handleDecrement = async (productId: number): Promise<void> => {
    setUpdatingItems(prev => new Set(prev).add(productId));
    try {
      await updateQuantity(productId, 'decrement');
    } catch (error) {
      alert('Ошибка при уменьшении количества');
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(productId);
        return newSet;
      });
    }
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

          {error && (
            <div className="error-message" style={{
              backgroundColor: '#ffebee',
              color: '#c62828',
              padding: '15px',
              borderRadius: '4px',
              margin: '10px 0',
              border: '1px solid #ef9a9a',
              whiteSpace: 'pre-line'
            }}>
              <strong>Ошибка:</strong> {error}
            </div>
          )}

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
                      <td align="center">
                        <div className="quantity-controls">
                          <button
                            onClick={() => handleDecrement(item.product_id)}
                            disabled={updatingItems.has(item.product_id)}
                            className="quantity-btn decrement"
                            aria-label="Уменьшить количество"
                          >
                            −
                          </button>
                          <span className="quantity-value">
                            {updatingItems.has(item.product_id) ? '...' : item.quantity}
                          </span>
                          <button
                            onClick={() => handleIncrement(item.product_id)}
                            disabled={updatingItems.has(item.product_id)}
                            className="quantity-btn increment"
                            aria-label="Увеличить количество"
                          >
                            +
                          </button>
                        </div>
                      </td>
                      <td align="right">{item.price} €</td>
                      <td align="right">
                        {(item.price * item.quantity).toFixed(2)} €
                      </td>
                    </tr>
                  ))}
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
                  disabled={isCheckingOut || cart.length === 0}
                >
                  {isCheckingOut ? (
                    'Перенаправление на оплату...'
                  ) : (
                    'Оплатить'
                  )}
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
