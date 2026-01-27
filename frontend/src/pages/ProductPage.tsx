import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getProductById } from "../api/products";
import "../styles/products/ProductCart.css";

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
    <div className="product-page">
      <h1>{product.name}</h1>
      <p className="category">Category: {product.category.name}</p>
      <p className="description">{product.description}</p>
      <p className="price">{product.price} €</p>
    </div>
  );
};

export default ProductPage;
