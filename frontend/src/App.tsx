import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import ProductPage from "./pages/ProductPage";
import { useAuth } from "./context/AuthContext";

const App: React.FC = () => {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/"
        element={user ? <HomePage /> : <Navigate to="/login" replace />}
      />

      <Route
        path="/products/:id"
        element={user ? <ProductPage /> : <Navigate to="/login" replace />}
      />
    </Routes>
  );
};

export default App;
