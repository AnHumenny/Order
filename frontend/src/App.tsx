import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

const LoginPage = () => {
  return (
    <div style={{ padding: 40 }}>
      <h2 style={{ color: "green" }}>Login Page</h2>

      <form style={{ marginTop: 20 }}>
        <div>
          <input
            type="text"
            placeholder="username"
            style={{ display: "block", marginBottom: 10 }}
          />
        </div>

        <div>
          <input
            type="password"
            placeholder="password"
            style={{ display: "block", marginBottom: 10 }}
          />
        </div>

        <button type="submit">Login</button>
      </form>
    </div>
  );
};

const HomePage = () => {
  return (
    <div style={{ padding: 40 }}>
      <h2 style={{ color: "blue" }}>Home Page</h2>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<HomePage />} />
      </Routes>
    </Router>
  );
};

export default App;
