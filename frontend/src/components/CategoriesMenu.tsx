import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCategories } from "../api/categories";
import type { Category } from "../api/categories";
import "../styles/categories/CategoriesMenu.css";

const CategoriesMenu: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch((err) => console.error("Categories load error:", err));
  }, []);

  return (
    <div className="categories-menu">
      <h4>Categories</h4>
      <ul>
        {categories.map((cat) => (
          <li key={cat.id}>
            <Link to={`/categories/${cat.id}`}>{cat.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CategoriesMenu;
