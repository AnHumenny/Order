import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getProductById } from "../api/products";
import CategoriesMenu from "../components/CategoriesMenu";
import UserBox from "../components/UserBox";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useLogout } from "../hooks/useLogout";
import type { Product } from "../api/types";
import "../styles/products/ProductCart.css";
import "../styles/categories/CategoriesMenu.css";
import "../styles/auth/AuthUser.css";

const ProductPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [quantity, setQuantity] = useState<number>(1);
  const [isAdding, setIsAdding] = useState<boolean>(false);

  const { user } = useAuth();
  const { cart, addToCart, updateQuantity } = useCart();
  const logout = useLogout();

  useEffect(() => {
    if (!id) return;

    getProductById(Number(id))
      .then(setProduct)
      .catch((err) => console.error("Product load error:", err));
  }, [id]);

  const handleQuantityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    if (value >= 1) {
      setQuantity(value);
    }
  };

  const handleAddToCart = async () => {
    if (!user) {
      alert("Необходимо войти в систему");
      return;
    }

    setIsAdding(true);
    try {
      await addToCart({
        id: product!.id,
        product_id: product!.id,
        name: product!.name,
        price: Number(product!.price),
        quantity: quantity,
      });
      alert(`Товар добавлен в корзину (${quantity} шт.)`);
      setQuantity(1);
    } catch (error) {
      alert("Ошибка при добавлении в корзину");
    } finally {
      setIsAdding(false);
    }
  };

  if (!product) return <div>Loading...</div>;

  return (
    <div className="home-container">
      <UserBox user={user} cart={cart} onLogout={logout} />

      <div style={{ marginTop: "50px" }} />

      <div className="content-wrapper">
        <CategoriesMenu />

        <div className="product-page-content">
          <h3>{product.name}</h3>

          {product.category && (
            <p className="category">
              Category: {product.category.name}
            </p>
          )}

          <p className="description">{product.description}</p>
          <p className="price">{product.price} €</p>

          {user && (
            <div>
              <div className="quantity-selector">
                <label htmlFor="quantity">Количество:</label>
                <input
                  type="number"
                  id="quantity"
                  min="1"
                  max="99"
                  value={quantity}
                  onChange={handleQuantityChange}
                  className="quantity-input"
                />
              </div>

              <button
                className="add-to-cart-btn"
                onClick={handleAddToCart}
                disabled={isAdding}
              >
                {isAdding ? 'Добавление...' : `В корзину (${quantity} шт.)`}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductPage;