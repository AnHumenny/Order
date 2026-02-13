import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import CategoriesMenu from "../components/CategoriesMenu";
import { getProducts } from "../api/products";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useLogout } from "../hooks/useLogout";
import { truncate } from "../utils/text";
import "../styles/products/ProductsGrid.css";
import "../styles/categories/CategoriesMenu.css";
import "../styles/auth/AuthUser.css";
import type { Product } from "../api/types";

const HomePage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);

  const { user } = useAuth();
  const { cart, addToCart } = useCart();
  const logout = useLogout();

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch((err) => console.error("Products load error:", err));
  }, []);

  return (
    <div className="home-container">
      <div className="user-box">
        {!user && (
          <Link to="/login" className="login-link">
            Авторизация
          </Link>
        )}
      </div>

      {user && (
        <div className="user-box">
          <Link to="/cart" className="cart-link">
            Корзина ({cart.length})
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

      <div className="content-wrapper">
        <CategoriesMenu />

        <div className="products-grid">
          {products.map((product) => (
            <div key={product.id} className="product-card">
              <Link to={`/products/${product.id}`} className="product-link">
                <h3>{product.name}</h3>
              </Link>

              {product.category && (
                <p className="category">
                  Category: {product.category.name}
                </p>
              )}

              <p className="description">
                {truncate(product.description, 10)}
              </p>

              <p className="price">{product.price} €</p>

              {user && (
                <button
                  className="add-to-cart-btn"
                  onClick={() =>
                    addToCart({
                      id: product.id,
                      name: product.name,
                      price: Number(product.price),
                      quantity: 1,
                    })
                  }
                >
                  В корзину
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomePage;
