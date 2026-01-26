import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useLogout } from "../hooks/useLogout";
import { getProducts } from "../api/products";
import "../styles/auth/AuthUser.css";
import "../styles/products/ProductsGrid.css";
import { truncate } from "../utils/text";

interface Product {
  id: number;
  name: string;
  description: string;
  price: string;
  category: {
    id: number;
    name: string;
  };
}

const HomePage: React.FC = () => {
  const { user } = useAuth();
  const logout = useLogout();
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch((err) => console.error("Products load error:", err));
  }, []);

  return (
    <>
      <div className="user-box">
        <span>Hi, {user?.username}</span>
        <button onClick={logout}>Logout</button>
      </div>

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
    </>
  );
};

export default HomePage;
