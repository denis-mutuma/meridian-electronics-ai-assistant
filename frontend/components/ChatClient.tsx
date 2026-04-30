"use client";

import { FormEvent, useState } from "react";

import { sendChat } from "../lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatClient() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSend = async (event: FormEvent) => {
    event.preventDefault();
    if (!input.trim()) {
      return;
    }

    const message = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setLoading(true);
    setError("");

    try {
      const reply = await sendChat(message);
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
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          Send
        </button>
      </form>

      {error && <p style={{ color: "#b42318" }}>{error}</p>}
    </main>
  );
}
