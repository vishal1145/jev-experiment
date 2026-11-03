import { useEffect, useMemo, useState } from "react";
import {
  getTickets,
  createTicket,
  updateTicketStatus
} from "./services/api";


const initialForm = {
  customer_name: "",
  email: "",
  subject: "",
  message: ""
};

function StatCard({ label, value, detail, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span className="stat-icon">{icon}</span>
        <span className="stat-detail">{detail}</span>
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function App() {
  const [form, setForm] = useState(initialForm);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function loadTickets() {
    try {
      const data = await getTickets();
      setTickets(data.tickets || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTickets();
  }, []);

  const stats = useMemo(() => {
    const open = tickets.filter(
      t => t.status === "Open"
    ).length;

    const review = tickets.filter(
      t => t.requires_human_review
    ).length;

    const average = tickets.length
      ? tickets.reduce(
          (sum, t) => sum + Number(t.urgency_score || 0),
          0
        ) / tickets.length
      : 0;

    return {
      total: tickets.length,
      open,
      review,
      average: average.toFixed(1)
    };
  }, [tickets]);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm(current => ({
      ...current,
      [name]: value
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setNotice("");
    setSubmitting(true);

    try {
      const result = await createTicket(form);

      setTickets(current => [
        result.ticket,
        ...current
      ]);

      setForm(initialForm);
      setNotice("Jev successfully analyzed your support ticket.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusChange(id, status) {
    try {
      const result = await updateTicketStatus(id, status);

      setTickets(current =>
        current.map(ticket =>
          ticket.id === id ? result.ticket : ticket
        )
      );

      setNotice(`Ticket #${id} updated.`);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  function formatDate(date) {
    return new Date(`${date.replace(" ", "T")}Z`)
      .toLocaleString();
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">S</div>
          <div>
            <div className="brand-name">SmartDesk<span>AI</span></div>
            <div className="brand-subtitle">SUPPORT INTELLIGENCE</div>
          </div>
        </div>

        <div className="topbar-right">
          <span className="online-dot"></span>
          <span>Jev AI integration</span>
          <span className="version">DEMO v1.0</span>
        </div>
      </header>

      <main className="container">

        <section className="hero">
          <div>
            <div className="eyebrow">INTELLIGENT TICKET MANAGEMENT</div>
            <h1>Support, made <span>smarter.</span></h1>
            <p>
              Let Jev evaluate incoming tickets, identify urgency
              and decide when a human should step in.
            </p>
          </div>

          <div className="hero-chip">
            <div className="hero-chip-icon">✦</div>
            <div>
              <strong>Powered by Jev</strong>
              <small>Choice · Score · Noul</small>
            </div>
          </div>
        </section>

        {error && (
          <div className="alert error-alert">
            <span>!</span> {error}
          </div>
        )}

        {notice && (
          <div className="alert success-alert">
            <span>✓</span> {notice}
          </div>
        )}

        <section className="stats-grid">
          <StatCard
            label="Total tickets"
            value={stats.total}
            detail="All records"
            icon="▤"
          />
          <StatCard
            label="Open tickets"
            value={stats.open}
            detail="Awaiting action"
            icon="◷"
          />
          <StatCard
            label="Human review"
            value={stats.review}
            detail="Jev recommended"
            icon="◎"
          />
          <StatCard
            label="Average urgency"
            value={`${stats.average}/5`}
            detail="Jev score"
            icon="↗"
          />
        </section>

        <section className="workspace">

          <div className="panel form-panel">
            <div className="panel-heading">
              <div>
                <div className="eyebrow">NEW REQUEST</div>
                <h2>Create support ticket</h2>
                <p>Submit a message for Jev to analyze.</p>
              </div>
              <div className="heading-icon">＋</div>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="field">
                  <label>Customer name *</label>
                  <input
                    name="customer_name"
                    value={form.customer_name}
                    onChange={handleChange}
                    placeholder="e.g. Rahul Sharma"
                    maxLength="100"
                    required
                  />
                </div>

                <div className="field">
                  <label>Email address</label>
                  <input
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="rahul@example.com"
                    maxLength="150"
                  />
                </div>
              </div>

              <div className="field">
                <label>Ticket subject *</label>
                <input
                  name="subject"
                  value={form.subject}
                  onChange={handleChange}
                  placeholder="Briefly describe the problem"
                  maxLength="150"
                  required
                />
              </div>

              <div className="field">
                <label>Describe the issue *</label>
                <textarea
                  name="message"
                  value={form.message}
                  onChange={handleChange}
                  placeholder="Explain what happened and what help is needed..."
                  rows="5"
                  maxLength="5000"
                  required
                />
                <div className="field-foot">
                  <span>Be clear and descriptive for better analysis.</span>
                  <span>{form.message.length}/5000</span>
                </div>
              </div>

              <button
                className="submit-button"
                type="submit"
                disabled={submitting}
              >
                {submitting ? (
                  <>Analyzing with Jev <span className="spinner"></span></>
                ) : (
                  <>✦ Analyze ticket with Jev <span>→</span></>
                )}
              </button>

              <div className="privacy-note">
                Your Jev API key stays on the Flask backend.
              </div>
            </form>
          </div>

          <aside className="panel explain-panel">
            <div className="eyebrow">HOW IT WORKS</div>
            <h2>Three decisions.<br />One smart workflow.</h2>
            <p className="explain-intro">
              Jev processes the ticket and returns structured
              decisions your application can use.
            </p>

            <div className="decision-item">
              <div className="decision-number choice-number">01</div>
              <div>
                <strong>Choice</strong>
                <p>Find the right department for the ticket.</p>
                <span className="decision-output">
                  Billing · Technical · Account · General
                </span>
              </div>
            </div>

            <div className="decision-item">
              <div className="decision-number score-number">02</div>
              <div>
                <strong>Score</strong>
                <p>Measure urgency against a defined scale.</p>
                <span className="decision-output">
                  Very Low → Critical
                </span>
              </div>
            </div>

            <div className="decision-item">
              <div className="decision-number noul-number">03</div>
              <div>
                <strong>Noul</strong>
                <p>Estimate whether human review is required.</p>
                <span className="decision-output">
                  Yes-probability from 0 to 1
                </span>
              </div>
            </div>

            <div className="logic-note">
              <span>⚡</span>
              <div>
                <strong>Application logic</strong>
                <p>
                  Tickets with a human-review probability of 65%
                  or more are flagged for review.
                </p>
              </div>
            </div>
          </aside>
        </section>

        <section className="panel tickets-panel">
          <div className="tickets-heading">
            <div>
              <div className="eyebrow">WORKSPACE</div>
              <h2>Recent support tickets</h2>
              <p>Jev's decisions and ticket management status.</p>
            </div>
            <button className="refresh-button" onClick={loadTickets}>
              ↻ Refresh
            </button>
          </div>

          {loading ? (
            <div className="empty-state">Loading tickets...</div>
          ) : tickets.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">▤</div>
              <strong>No tickets yet</strong>
              <p>Create your first ticket to see Jev in action.</p>
            </div>
          ) : (
            <div className="ticket-list">
              {tickets.map(ticket => (
                <article className="ticket-card" key={ticket.id}>
                  <div className="ticket-main">
                    <div className="ticket-id">
                      TICKET #{String(ticket.id).padStart(4, "0")}
                    </div>

                    <h3>{ticket.subject}</h3>
                    <p className="ticket-customer">
                      {ticket.customer_name}
                      {ticket.email && ` · ${ticket.email}`}
                    </p>

                    <p className="ticket-message">
                      {ticket.message}
                    </p>

                    <div className="ticket-meta">
                      <span className="category-tag">
                        {ticket.category}
                      </span>

                      {ticket.requires_human_review ? (
                        <span className="review-tag">
                          Human review
                        </span>
                      ) : (
                        <span className="normal-tag">
                          Standard review
                        </span>
                      )}

                      <span className="ticket-date">
                        {formatDate(ticket.created_at)}
                      </span>
                    </div>
                  </div>

                  <div className="ticket-analysis">
                    <div className="analysis-label">URGENCY SCORE</div>
                    <div className="score-display">
                      {Number(ticket.urgency_score).toFixed(1)}
                      <small>/5</small>
                    </div>

                    <div className="score-track">
                      <div
                        className="score-fill"
                        style={{
                          width: `${(ticket.urgency_score / 5) * 100}%`
                        }}
                      />
                    </div>

                    <div className="urgency-label">
                      {ticket.urgency_label}
                    </div>

                    <div className="probability-label">
                      Human review probability
                    </div>
                    <strong>
                      {(ticket.escalation_probability * 100).toFixed(1)}%
                    </strong>

                    <div className="status-control">
                      <label htmlFor={`status-${ticket.id}`}>
                        STATUS
                      </label>
                      <select
                        id={`status-${ticket.id}`}
                        value={ticket.status}
                        onChange={event =>
                          handleStatusChange(
                            ticket.id,
                            event.target.value
                          )
                        }
                      >
                        <option>Open</option>
                        <option>In Progress</option>
                        <option>Resolved</option>
                      </select>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <footer>
          <strong>SmartDesk AI</strong>
          <span>Built with Flask · React · SQLite · Jev TypeSafe AI</span>
          <span>College Learning Project</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
