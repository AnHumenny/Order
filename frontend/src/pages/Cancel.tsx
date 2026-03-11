import React from "react";
import { useNavigate } from "react-router-dom";

const Cancel: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div style={{
      textAlign: 'center',
      padding: '50px',
      maxWidth: '600px',
      margin: '0 auto'
    }}>
      <div style={{ fontSize: '80px', marginBottom: '20px' }}>❌</div>
      <h1 style={{ color: '#c62828', marginBottom: '20px' }}>
        Оплата отменена
      </h1>
      <p style={{ fontSize: '18px', marginBottom: '30px', color: '#555' }}>
        Вы можете продолжить покупки и оформить заказ позже.
      </p>
      <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
        <button
          onClick={() => navigate('/cart')}
          style={{
            padding: '12px 30px',
            fontSize: '16px',
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            transition: 'background-color 0.3s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#1976D2'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#2196F3'}
        >
          Вернуться в корзину
        </button>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '12px 30px',
            fontSize: '16px',
            backgroundColor: '#757575',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            transition: 'background-color 0.3s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#616161'}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#757575'}
        >
          На главную
        </button>
      </div>
    </div>
  );
};

export default Cancel;
