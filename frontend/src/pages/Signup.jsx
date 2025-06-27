import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [pass1, setPass1] = useState("");
  const [pass2, setPass2] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSignup = async () => {
    if (pass1 !== pass2) {
      setError("Passwords do not match.");
      return;
    }
    try {
      const res = await fetch("http://localhost:5000/signup", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password: pass1, is_organization: false }),
      });
      const data = await res.json();
      if (res.ok) {
        navigate("/chat");
      } else {
        setError(data.error || "Signup failed.");
      }
    } catch (e) {
      setError("Network error");
    }
  };

  return (
    <div className="form-container">
      <h2>Sign Up</h2>
      <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <input type="password" placeholder="Password" value={pass1} onChange={e => setPass1(e.target.value)} />
      <input type="password" placeholder="Confirm Password" value={pass2} onChange={e => setPass2(e.target.value)} />
      <button onClick={handleSignup}>Create Account</button>
      <p className="error">{error}</p>
      <p>Already have an account? <Link to="/login">Login</Link></p>
    </div>
  );
}
