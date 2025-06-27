import React, { useState, useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar.jsx";

export default function ChatDashboard() {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const logRef = useRef();

  const sendQuery = async () => {
    if (!query.trim()) return;
    setMessages(prev => [...prev, { role: "user", content: query }]);
    setQuery("");

    const res = await fetch("http://localhost:5000/query", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await res.json();
    setMessages(prev => [...prev, { role: "bot", content: data.response || "No answer." }]);
  };

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="dashboard">
      <Sidebar />
      <div className="chat-container">
        <div className="chat-log" ref={logRef}>
          {messages.map((m, i) => (
            <div key={i} className={`msg ${m.role}`}>{m.content}</div>
          ))}
        </div>
        <div className="chat-input">
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Ask something..." />
          <button onClick={sendQuery}>Send</button>
        </div>
      </div>
    </div>
  );
}
