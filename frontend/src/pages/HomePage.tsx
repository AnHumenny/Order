import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import CategoriesMenu from "../components/CategoriesMenu";
import { getProducts } from "../api/products";
import { truncate } from "../utils/text";
import "../styles/products/ProductsGrid.css";

interface Product {
  id: number;
  name: string;
  description: string;
  price: string;
  category?: {
    id: number;
    name: string;
  };
}

const HomePage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch((err) => console.error("Products load error:", err));
  }, []);

return (
  <div className="home-container">
    <div className="top-bar" align="right">
      <Link to="/login" className="login-link">
        Личный кабинет
      </Link>
    </div>

    <div className="content-wrapper">
      <CategoriesMenu />

      <div className="products-grid">
        {products.map((product) => (
          <Link
            key={product.id}
            to={`/products/${product.id}`}
            className="product-link"
          >
            <div className="product-card">
              <h3>{product.name}</h3>
              <p className="category">Category: {product.category.name}</p>
              <p className="description">
                {truncate(product.description, 10)}
              </p>
              <p className="price">{product.price} €</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  </div>
);

};

export default HomePage;
