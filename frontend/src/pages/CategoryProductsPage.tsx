import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getProductsByCategory } from "../api/productsByCategory";
import type { Product } from "../api/types";
import { truncate } from "../utils/text";
import "../styles/products/ProductsGrid.css";
import "../styles/categories/CategoriesMenu.css";
import "../styles/auth/AuthUser.css";
import CategoriesMenu from "../components/CategoriesMenu";
import { useAuth } from "../context/AuthContext";
import { useLogout } from "../hooks/useLogout";

const CategoryProductsPage: React.FC = () => {
  const { category_id } = useParams<{ category_id: string }>();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const { user } = useAuth();
  const logout = useLogout();

  useEffect(() => {
    if (!category_id) return;

    getProductsByCategory(Number(category_id))
      .then(setProducts)
      .finally(() => setLoading(false));
  }, [category_id]);

  if (loading) return <p>Loading products...</p>;

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

        <div className="products-grid">
          {products.length === 0 ? (
            <p>No products in this category.</p>
          ) : (
            products.map((product) => (
              <Link
                key={product.id}
                to={`/products/${product.id}`}
                className="product-link"
              >
                <div className="product-card">
                  <h3>{product.name}</h3>
                  <p className="description">
                    {truncate(product.description, 12)}
                  </p>
                  <p className="price">{product.price} €</p>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default CategoryProductsPage;
