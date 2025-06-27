// src/components/Navbar.jsx
import React from "react";
import { useNavigate } from "react-router-dom";

const Navbar = () => {
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("uuid");
    navigate("/");
  };

  return (
    <div className="navbar">
      <h2>RAG Assistant</h2>
      <div className="nav-buttons">
        <button onClick={() => navigate("/chat")}>Chat</button>
        <button onClick={logout}>Logout</button>
      </div>
    </div>
  );
};

export default Navbar;
