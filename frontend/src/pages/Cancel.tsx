import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/cart/CartPage.css";

const Cancel: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/cart');
    }, 5000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="payment-status-container">
      <div className="payment-status-icon">❌</div>
      <h4 className="payment-status-title cancel">
        Оплата отменена
      </h4>
      <p className="payment-status-message">
        Вы можете продолжить покупки и оформить заказ позже.
      </p>
      <p className="payment-status-timer">
        Возврат в корзину через 5 секунд...
      </p>
      <div className="payment-status-buttons">
        <button
          onClick={() => navigate('/cart')}
          className="payment-status-btn payment-status-btn-secondary"
        >
          Вернуться в корзину
        </button>
        <button
          onClick={() => navigate('/')}
          className="payment-status-btn payment-status-btn-tertiary"
        >
          На главную
        </button>
      </div>
    </div>
  );
};

export default Cancel;
