// src/pages/Chatbot.jsx
import React, { useState } from "react";
import Navbar from "../components/Navbar";
import FileManager from "../components/FileManager";

const Chatbot = () => {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);

  const sendQuery = async () => {
    const uuid = localStorage.getItem("uuid");
    if (!query.trim()) return;

    const newMessage = { role: "user", content: query };
    setMessages((prev) => [...prev, newMessage]);

    const res = await fetch("http://localhost:5000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uuid, query }),
    });

    const data = await res.json();
    setMessages((prev) => [...prev, { role: "bot", content: data.response || "No response." }]);
    setQuery("");
  };

  return (
    <>
      <Navbar />
      <div className="chat-window">
        <div className="chat-messages">
          {messages.map((m, idx) => (
            <div key={idx} className={`message ${m.role}`}>
              <strong>{m.role === "user" ? "You: " : "Bot: "}</strong> {m.content}
            </div>
          ))}
        </div>
        <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ask something..." />
        <button onClick={sendQuery}>Send</button>
      </div>

      <FileManager />
    </>
  );
};

export default Chatbot;
