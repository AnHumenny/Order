import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getProductsByCategory } from "../api/productsByCategory";
import type { Product } from "../api/types";
import { truncate } from "../utils/text";
import "../styles/products/ProductsGrid.css";
import "../styles/categories/CategoriesMenu.css";
import "../styles/auth/AuthUser.css";
import CategoriesMenu from "../components/CategoriesMenu";
import UserBox from "../components/UserBox";
import { useAuth } from "../context/AuthContext";
import { useLogout } from "../hooks/useLogout";
import { useCart } from "../context/CartContext";

const CategoryProductsPage: React.FC = () => {
  const { category_id } = useParams<{ category_id: string }>();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const { user } = useAuth();
  const logout = useLogout();
  const { cart, addToCart } = useCart();

  useEffect(() => {
    if (!category_id) return;

    setLoading(true);
    getProductsByCategory(Number(category_id))
      .then(setProducts)
      .finally(() => setLoading(false));
  }, [category_id]);

  if (loading) {
    return <p style={{ padding: 20 }}>Loading products...</p>;
  }

  return (
    <div className="home-container">
      <UserBox user={user} cart={cart} onLogout={logout} />

      <div className="content-wrapper">
        <CategoriesMenu />

        <div className="products-grid">
          {products.length === 0 ? (
            <p>No products in this category.</p>
          ) : (
            products.map((product) => (
              <div key={product.id} className="product-card">
                <Link
                  to={`/products/${product.id}`}
                  className="product-link"
                >
                  <h3>{product.name}</h3>
                  <p className="description">
                    {truncate(product.description, 12)}
                  </p>
                  <p className="price">{product.price} €</p>
                </Link>

                <button
                  className="add-to-cart-btn"
                  onClick={() =>
                    addToCart({
                      id: product.id,
                      product_id: product.id,
                      name: product.name,
                      price: Number(product.price),
                      quantity: 1,
                    })
                  }
                >
                  В корзину
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default CategoryProductsPage;
