import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import ProductPage from "./pages/ProductPage";
import CategoriesMenu from "./components/CategoriesMenu";
// import { useAuth } from "./context/AuthContext";

const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/products/:id" element={<ProductPage />} />
      <Route path="/login" element={<LoginPage />} />
    </Routes>
  );
};

export default App;

//       <Route path="/categories/:id" element={<CategoriesPage />} />