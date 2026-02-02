import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getProductById } from "../api/products";
import CategoriesMenu from "../components/CategoriesMenu";
import "../styles/products/ProductCart.css";
import "../styles/categories/CategoriesMenu.css";
import "../styles/auth/AuthUser.css";
import type { Product } from "./types";
import { useAuth } from "../context/AuthContext";
import { useLogout } from "../hooks/useLogout";

const ProductPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);

  const { user } = useAuth();
  const logout = useLogout();

  useEffect(() => {
    if (!id) return;

    getProductById(Number(id))
      .then(setProduct)
      .catch((err) => console.error("Product load error:", err));
  }, [id]);

  if (!product) return <div>Loading...</div>;

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

        <div className="product-page-content">
          <h3>{product.name}</h3>
          <p className="category">Category: {product.category.name}</p>
          <p className="description">{product.description}</p>
          <p className="price">{product.price} $</p>
        </div>
      </div>
    </div>
  );
};

export default ProductPage;
