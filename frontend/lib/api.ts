// NEXT_PUBLIC_ prefix is required for the variable to be inlined at build time
// when Next.js generates a static export. Without this prefix, the value would
// be undefined in the browser.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function sendChat(customerEmail: string, message: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ customer_email: customerEmail, message }),
  });

  if (!response.ok) {
    throw new Error("Failed to send message");
  }

  const data = (await response.json()) as { reply: string };
  return data.reply;
}
