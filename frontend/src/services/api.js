const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers
    }
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || "Something went wrong.");
  }

  return data;
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

