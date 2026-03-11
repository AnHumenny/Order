import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Success: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/');
    }, 3000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div style={{
      textAlign: 'center',
      padding: '50px',
      maxWidth: '600px',
      margin: '0 auto'
    }}>
      <div style={{ fontSize: '80px', marginBottom: '20px' }}>✅</div>
      <h1 style={{ color: '#2e7d32', marginBottom: '20px' }}>
        Оплата прошла успешно!
      </h1>
      <p style={{ fontSize: '18px', marginBottom: '30px', color: '#555' }}>
        Спасибо за покупку! Ваш заказ оформлен.
      </p>
      <p style={{ color: '#777', marginBottom: '30px' }}>
        Вы будете перенаправлены на главную через 3 секунды...
      </p>
      <button
        onClick={() => navigate('/')}
        style={{
          padding: '12px 30px',
          fontSize: '16px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          transition: 'background-color 0.3s'
        }}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#45a049'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#4CAF50'}
      >
        Вернуться на главную
      </button>
    </div>
  );
};

export default Success;
