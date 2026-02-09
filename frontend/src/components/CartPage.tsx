import React from "react";
import { useCart } from "../context/CartContext";

const CartPage: React.FC = () => {
  const { cart } = useCart();

  return (
    <div style={{ padding: 20 }}>
      <h3>Корзина</h3>
      {cart.length === 0 ? (
        <p>Ваша корзина пуста.</p>
      ) : (
        <ul>
          {cart.map((item) => (
            <li key={item.id}>
              {item.name} — {item.quantity} × {item.price} €
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default CartPage;
