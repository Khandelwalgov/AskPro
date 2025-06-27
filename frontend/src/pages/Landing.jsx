import React from "react";
import { useNavigate } from "react-router-dom";

export default function Landing() {
  const nav = useNavigate();
  return (
    <div className="landing">
      <div className="hero">
        <h1>Smart RAG Chatbot</h1>
        <p>Upload your documents and chat with your content using AI.</p>
        <button onClick={() => nav("/login")}>Login</button>
        <button className="secondary" onClick={() => nav("/signup")}>Sign Up</button>
      </div>
    </div>
  );
}
