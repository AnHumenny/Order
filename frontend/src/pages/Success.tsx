import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/cart/CartPage.css";

const Success: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/');
    }, 5000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="payment-status-container">
      <div className="payment-status-icon">✅</div>
      <h4 className="payment-status-title success">
        Оплата прошла успешно!
      </h4>
      <p className="payment-status-message">
        Спасибо за покупку! Ваш заказ оформлен.
      </p>
      <p className="payment-status-timer">
        Вы будете перенаправлены на главную через 5 секунд...
      </p>
      <button
        onClick={() => navigate('/')}
        className="payment-status-btn payment-status-btn-primary"
      >
        Вернуться на главную
      </button>
    </div>
  );
};

export default Success;
