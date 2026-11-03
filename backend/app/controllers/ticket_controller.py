from flask import request, jsonify, current_app

from ..models.ticket import (
    create_ticket,
    get_all_tickets,
    update_ticket_status
)

from ..services.jev_service import (
    analyze_ticket,
    JevServiceError
)


VALID_STATUSES = [
    "Open",
    "In Progress",
    "Resolved"
]


def health():
    return jsonify({
        "success": True,
        "message": "SmartDesk AI backend is running."
    })


def list_tickets():
    tickets = get_all_tickets(
        current_app.config["DATABASE"]
    )

    return jsonify({
        "success": True,
        "tickets": tickets
    })


def create_new_ticket():
    data = request.get_json(silent=True) or {}

    customer_name = str(
        data.get("customer_name", "")
    ).strip()

    email = str(
        data.get("email", "")
    ).strip()

    subject = str(
        data.get("subject", "")
    ).strip()

    message = str(
        data.get("message", "")
    ).strip()

    if not customer_name or not subject or not message:
        return jsonify({
            "success": False,
            "error": "Name, subject and message are required."
        }), 400

    if len(subject) > 150 or len(message) > 5000:
        return jsonify({
            "success": False,
            "error": "Subject or message exceeds the allowed length."
        }), 400

    ticket_data = {
        "customer_name": customer_name,
        "email": email,
        "subject": subject,
        "message": message
    }

    try:
        # Business logic: ask Jev to analyze the ticket.
        analysis = analyze_ticket(ticket_data)

        # Persist the result only after successful analysis.
        ticket = create_ticket(
            current_app.config["DATABASE"],
            ticket_data,
            analysis
        )

        return jsonify({
            "success": True,
            "message": "Ticket analyzed successfully.",
            "ticket": ticket
        }), 201

    except JevServiceError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 502


def change_ticket_status(ticket_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in VALID_STATUSES:
        return jsonify({
            "success": False,
            "error": "Invalid ticket status."
        }), 400

    ticket = update_ticket_status(
        current_app.config["DATABASE"],
        ticket_id,
        status
    )

    if ticket is None:
        return jsonify({
            "success": False,
            "error": "Ticket not found."
        }), 404

    return jsonify({
        "success": True,
        "ticket": ticket
    })
