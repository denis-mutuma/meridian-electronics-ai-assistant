// NEXT_PUBLIC_ prefix is required for the variable to be inlined at build time
// when Next.js generates a static export. Without this prefix, the value would
// be undefined in the browser.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

export class ChatApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ChatApiError";
  }
}

export type ChatHistoryMessage = {
  role: "user" | "assistant";
  content: string;
};

async function readErrorDetail(response: Response): Promise<string> {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string" && body.detail.trim()) {
        return body.detail;
      }
      if (body.detail) {
        return JSON.stringify(body.detail);
      }
    } catch {
      return response.statusText || "Request failed";
    }
  }

  try {
    const text = await response.text();
    return text.trim() || response.statusText || "Request failed";
  } catch {
    return response.statusText || "Request failed";
  }
}

export async function sendChat(
  customerEmail: string,
  message: string,
  history: ChatHistoryMessage[] = [],
  signal?: AbortSignal,
): Promise<string> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ customer_email: customerEmail, message, history }),
      signal,
    });
  } catch (exc) {
    if (exc instanceof DOMException && exc.name === "AbortError") {
      throw new ChatApiError("request cancelled");
    }
    throw new ChatApiError("network error");
  }

  if (!response.ok) {
    const detail = await readErrorDetail(response);
    throw new ChatApiError(`${response.status} ${detail}`, response.status);
  }

  const data = (await response.json()) as { reply: string };
  if (typeof data.reply !== "string") {
    throw new ChatApiError("invalid response from chat service");
  }

  return data.reply;
}
