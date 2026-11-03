import sqlite3
import json


def get_connection(database):
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database):
    with get_connection(database) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                email TEXT,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,

                category TEXT NOT NULL,
                category_confidence REAL,

                urgency_score REAL,
                urgency_label TEXT,
                urgency_confidence REAL,

                escalation_probability REAL,
                requires_human_review INTEGER,

                status TEXT DEFAULT 'Open',
                analysis_json TEXT,

                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def serialize_ticket(row):
    if row is None:
        return None

    ticket = dict(row)

    ticket["requires_human_review"] = bool(
        ticket["requires_human_review"]
    )

    ticket["analysis"] = json.loads(
        ticket.pop("analysis_json") or "{}"
    )

    return ticket


def create_ticket(database, ticket, analysis):
    with get_connection(database) as conn:
        cursor = conn.execute("""
            INSERT INTO tickets (
                customer_name,
                email,
                subject,
                message,
                category,
                category_confidence,
                urgency_score,
                urgency_label,
                urgency_confidence,
                escalation_probability,
                requires_human_review,
                status,
                analysis_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', ?)
        """, (
            ticket["customer_name"],
            ticket.get("email", ""),
            ticket["subject"],
            ticket["message"],
            analysis["category"],
            analysis["category_confidence"],
            analysis["urgency_score"],
            analysis["urgency_label"],
            analysis["urgency_confidence"],
            analysis["escalation_probability"],
            int(analysis["requires_human_review"]),
            json.dumps(analysis)
        ))

        ticket_id = cursor.lastrowid
        conn.commit()

        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

        return serialize_ticket(row)


def get_all_tickets(database):
    with get_connection(database) as conn:
        rows = conn.execute("""
            SELECT * FROM tickets
            ORDER BY id DESC
        """).fetchall()

        return [serialize_ticket(row) for row in rows]


def update_ticket_status(database, ticket_id, status):
    with get_connection(database) as conn:
        cursor = conn.execute("""
            UPDATE tickets
            SET status = ?
            WHERE id = ?
        """, (status, ticket_id))

        conn.commit()

        if cursor.rowcount == 0:
            return None

        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()

        return serialize_ticket(row)

