import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const res = await fetch("http://localhost:5000/login", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password: pass }),
      });
      const data = await res.json();
      if (res.ok) {
        navigate("/chat");
      } else {
        setError(data.error || "Login failed.");
      }
    } catch (e) {
      setError("Network error");
    }
  };

  return (
    <div className="form-container">
      <h2>Login</h2>
      <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <input type="password" placeholder="Password" value={pass} onChange={e => setPass(e.target.value)} />
      <button onClick={handleLogin}>Login</button>
      <p className="error">{error}</p>
      <p>New here? <Link to="/signup">Sign Up</Link></p>
    </div>
  );
}
