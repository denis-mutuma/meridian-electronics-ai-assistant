"use client";

import { FormEvent, useRef, useState } from "react";

import { ChatHistoryMessage, sendChat } from "../lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  status?: "sending" | "failed" | "streaming";
};

const RECENT_HISTORY_LIMIT = 8;
const id = () => `${Date.now()}-${Math.random().toString(36).slice(2)}`;
const sleep = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms));

export default function HomePage() {
  const [email, setEmail] = useState("");
  const [emailConfirmed, setEmailConfirmed] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const abortRef = useRef<AbortController | null>(null);
  const streamRef = useRef(0);

  const history = (skipId?: string): ChatHistoryMessage[] =>
    messages
      .filter((m) => m.id !== skipId && m.status !== "failed")
      .slice(-RECENT_HISTORY_LIMIT)
      .map(({ role, content }) => ({ role, content }));

  const patchMessage = (messageId: string, patch: Partial<Message>) =>
    setMessages((prev) => prev.map((m) => (m.id === messageId ? { ...m, ...patch } : m)));

  const streamReply = async (reply: string, messageId: string, token: number) => {
    for (let i = 4; i < reply.length && streamRef.current === token; i += 4) {
      patchMessage(messageId, { content: reply.slice(0, i) });
      await sleep(18);
    }
    if (streamRef.current === token) {
      patchMessage(messageId, { content: reply, status: undefined });
    }
  };

  const sendMessage = async (raw: string, retryId?: string) => {
    const content = raw.trim();
    if (!content || loading) return;

    const userId = retryId ?? id();
    const controller = new AbortController();
    const token = streamRef.current + 1;
    abortRef.current = controller;
    streamRef.current = token;
    setInput("");
    setError("");
    setLoading(true);
    setMessages((prev) => {
      const userMessage: Message = { id: userId, role: "user", content, status: "sending" };
      return retryId ? prev.map((m) => (m.id === retryId ? userMessage : m)) : [...prev, userMessage];
    });

    try {
      const reply = await sendChat(email, content, history(retryId), controller.signal);
      const assistantId = id();
      patchMessage(userId, { status: undefined });
      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: "assistant", content: "", status: "streaming" },
      ]);
      await streamReply(reply, assistantId, token);
    } catch (exc) {
      const reason = exc instanceof Error ? exc.message : "unknown error";
      setError(reason === "request cancelled" ? "Chat request cancelled." : `Chat request failed: ${reason}`);
      patchMessage(userId, { status: "failed" });
    } finally {
      abortRef.current = null;
      setLoading(false);
    }
  };

  const handleEmailSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (email.trim()) setEmailConfirmed(true);
  };

  const handleSend = async (event: FormEvent) => {
    event.preventDefault();
    await sendMessage(input);
  };

  const cancel = () => {
    streamRef.current += 1;
    abortRef.current?.abort();
  };

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

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <h1>Meridian Electronics Assistant</h1>
      <p style={{ color: "#57606a" }}>Signed in as <strong>{email}</strong></p>

      <section
        aria-label="Chat messages"
        aria-live="polite"
        style={{
          border: "1px solid #d0d7de",
          borderRadius: 10,
          minHeight: 320,
          padding: 16,
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "78%",
              border: "1px solid #d0d7de",
              borderRadius: 8,
              padding: "10px 12px",
              background: m.role === "user" ? "#f6f8fa" : "#ffffff",
            }}
          >
            <div style={{ color: "#57606a", fontSize: 12, fontWeight: 700, marginBottom: 4 }}>
              {m.role === "user" ? "You" : "Assistant"}
              {m.status === "sending" && " - sending"}
              {m.status === "failed" && " - failed"}
              {m.status === "streaming" && " - typing"}
            </div>
            <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>
            {m.status === "failed" && (
              <button type="button" disabled={loading} onClick={() => sendMessage(m.content, m.id)} style={{ marginTop: 8 }}>
                Retry
              </button>
            )}
          </div>
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
        <button type="submit" disabled={loading || !input.trim()}>Send</button>
        {loading && <button type="button" onClick={cancel}>Cancel</button>}
      </form>

      {error && <p style={{ color: "#b42318" }}>{error}</p>}
    </main>
  );
}
