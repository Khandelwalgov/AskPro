import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/Landing.jsx";
import Signup from "./pages/Signup.jsx";
import Login from "./pages/Login.jsx";
import ChatDashboard from "./pages/ChatDashboard.jsx";

function App() {
  const isLoggedIn = document.cookie.includes("session=");
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/chat"
          element={<ChatDashboard />}/>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
