import React, { useState } from "react";
import FileManager from "./FileManager.jsx";
import { useNavigate } from "react-router-dom";

export default function Sidebar() {
  const [open, setOpen] = useState(true);
  const nav = useNavigate();

  const logout = async () => {
    await fetch("http://localhost:5000/logout", {
      method: "POST",
      credentials: "include"
    });
    nav("/login");
  };

  return (
    <div className={`sidebar ${open ? "expanded" : "collapsed"}`}>
      <button onClick={() => setOpen(!open)}>☰</button>
      {open && (
        <>
          <h3>Menu</h3>
          <FileManager />
          <button onClick={logout}>Logout</button>
        </>
      )}
    </div>
  );
}
