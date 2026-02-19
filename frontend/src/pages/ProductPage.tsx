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

  const { user } = useAuth();
  const { cart, addToCart } = useCart();
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
      </div>
    </div>
  );
};

export default ProductPage;
