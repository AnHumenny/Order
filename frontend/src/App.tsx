import React from "react";
import { Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import ProductPage from "./pages/ProductPage";
import CategoryProductsPage from "./pages/CategoryProductsPage";
import UserPage from "./pages/UserPage";
import CartPage from "./pages/CartPage";

const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/products/:id" element={<ProductPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/me" element={<UserPage />} />
      <Route path="/categories/:category_id" element={<CategoryProductsPage />} />
      <Route path="/cart" element={<CartPage />} />
    </Routes>
  );
};

export default App;
