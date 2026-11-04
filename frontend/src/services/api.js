let rawUrl = (import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api")
  .trim()
  .replace(/\/+$/, "");

// Automatically handle URLs with or without /api at the end
if (!rawUrl.endsWith("/api")) {
  rawUrl = `${rawUrl}/api`;
}

const API_URL = rawUrl;

async function request(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      }
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || `Server responded with status ${response.status}`);
    }

    return data;
  } catch (err) {
    if (err.name === "TypeError" && err.message === "Failed to fetch") {
      throw new Error(
        "Could not connect to backend. Please check if the Render backend service is awake and running."
      );
    }
    throw err;
  }
}

export const getTickets = () =>
  request("/tickets");

export const createTicket = (ticket) =>
  request("/tickets", {
    method: "POST",
    body: JSON.stringify(ticket)
  });

export const updateTicketStatus = (id, status) =>
  request(`/tickets/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status })
  });
