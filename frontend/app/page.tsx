"use client";

import { FormEvent, useState } from "react";

import { sendChat } from "../lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function HomePage() {
  // Email gate: the user must confirm their email before entering the chat.
  // The email is not stored in a session or cookie — it is passed as a plain
  // field on every request so the backend can look up the customer's data.
  const [email, setEmail] = useState("");
  const [emailConfirmed, setEmailConfirmed] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleEmailSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (email.trim()) {
      setEmailConfirmed(true);
    }
  };

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
      // Pass the confirmed email on every message — the backend uses it to
      // scope MCP tool calls to the correct customer.
      const reply = await sendChat(email, message);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (exc) {
      const reason = exc instanceof Error ? exc.message : "unknown error";
      setError(`Chat request failed: ${reason}`);
    } finally {
      setLoading(false);
    }
  };

  // Screen 1: email gate
  if (!emailConfirmed) {
    return (
      <main style={{ maxWidth: 480, margin: "80px auto", padding: 24 }}>
        <h1>Meridian Electronics Assistant</h1>
        <p>Enter your email address to start.</p>
        <form onSubmit={handleEmailSubmit} style={{ display: "flex", gap: 10 }}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            style={{ flex: 1 }}
          />
          <button type="submit">Continue</button>
        </form>
      </main>
    );
  }

  // Screen 2: chat
  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <h1>Meridian Electronics Assistant</h1>
      <p style={{ color: "#57606a" }}>Signed in as <strong>{email}</strong></p>

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
