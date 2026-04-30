"use client";

import { FormEvent, useState } from "react";

import { login, sendChat } from "../lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatClient() {
  // Login/session state.
  const [email, setEmail] = useState("");
  const [pin, setPin] = useState("");
  const [token, setToken] = useState("");

  // Chat interaction state.
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      const result = await login(email, pin);
      setToken(result.access_token);
    } catch {
      setError("Login failed. Use one of the seeded email + PIN pairs.");
    }
  };

  const handleSend = async (event: FormEvent) => {
    event.preventDefault();
    if (!input.trim() || !token) {
      return;
    }

    // Optimistically append the customer message before waiting for the reply.
    const message = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setLoading(true);
    setError("");

    try {
      const reply = await sendChat(message, token);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setError("Unable to send message right now.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <h1>Meridian Electronics Assistant</h1>
      {!token && (
        <form onSubmit={handleLogin} style={{ display: "grid", gap: 12, marginBottom: 24 }}>
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required />
          <input value={pin} onChange={(e) => setPin(e.target.value)} placeholder="PIN" required />
          <button type="submit">Sign in</button>
        </form>
      )}

      <section style={{ border: "1px solid #d0d7de", borderRadius: 10, minHeight: 320, padding: 16 }}>
        {messages.map((message, index) => (
          <p key={`${message.role}-${index}`}>
            <strong>{message.role === "user" ? "You" : "Assistant"}:</strong> {message.content}
          </p>
        ))}
        {loading && <p>Assistant is thinking...</p>}
      </section>

      <form onSubmit={handleSend} style={{ display: "flex", gap: 10, marginTop: 12 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about inventory, orders, or account"
          style={{ flex: 1 }}
          disabled={!token || loading}
        />
        <button type="submit" disabled={!token || loading}>
          Send
        </button>
      </form>

      {error && <p style={{ color: "#b42318" }}>{error}</p>}
    </main>
  );
}
