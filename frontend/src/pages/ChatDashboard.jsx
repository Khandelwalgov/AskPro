import React, { useState, useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar.jsx";

export default function ChatDashboard() {
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const logRef = useRef();

  const sendQuery = async () => {
    if (!query.trim()) return;

    // Show user's message
    setMessages(prev => [...prev, { role: "user", content: query }]);
    setQuery("");

    const uuid = localStorage.getItem("uuid");
    if (!uuid) {
      setMessages(prev => [...prev, {
        role: "bot",
        content: "⚠️ No user UUID found. Please log in again."
      }]);
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/query", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, uuid })
      });

      const data = await res.json();

      if (data.error) {
        setMessages(prev => [...prev, { role: "bot", content: `❌ ${data.error}` }]);
        return;
      }

      const chunks = data.chunks || [];
      const formattedChunks = chunks.length
        ? chunks.join("\n\n---\n\n")
        : "No relevant chunks found.";

      setMessages(prev => [...prev, { role: "bot", content: formattedChunks }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: "bot",
        content: "❌ Network or server error. Try again later."
      }]);
    }
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
            <div
              key={i}
              className={`msg ${m.role}`}
              style={{ whiteSpace: 'pre-wrap' }}
            >
              {m.content}
            </div>
          ))}
        </div>
        <div className="chat-input">
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && sendQuery()}
            placeholder="Ask something..."
          />
          <button onClick={sendQuery}>Send</button>
        </div>
      </div>
    </div>
  );
}
