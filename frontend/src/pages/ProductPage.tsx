import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getProductById } from "../api/products";
import CategoriesMenu from "../components/CategoriesMenu";
import "../styles/products/ProductCart.css";
import "../styles/categories/CategoriesMenu.css";

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

const ProductPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);

  useEffect(() => {
    if (!id) return;

    getProductById(Number(id))
      .then(setProduct)
      .catch((err) => console.error("Product load error:", err));
  }, [id]);

  if (!product) {
    return <div>Loading...</div>;
  }

  return (
    <div className="product-page-container">
      <CategoriesMenu />
      <div className="product-page-content">
        <h3>{product.name}</h3>
        <p className="category">Category: {product.category.name}</p>
        <p className="description">{product.description}</p>
        <p className="price">{product.price} $</p>
      </div>
    </div>
  );
};

export default ProductPage;
