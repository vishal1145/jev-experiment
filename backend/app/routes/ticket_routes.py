from flask import Blueprint

from ..controllers.ticket_controller import (
    health,
    list_tickets,
    create_new_ticket,
    change_ticket_status
)

ticket_bp = Blueprint("tickets", __name__)

ticket_bp.route("/health", methods=["GET"])(health)

ticket_bp.route(
    "/tickets",
    methods=["GET"]
)(list_tickets)

ticket_bp.route(
    "/tickets",
    methods=["POST"]
)(create_new_ticket)

ticket_bp.route(
    "/tickets/<int:ticket_id>/status",
    methods=["PATCH"]
)(change_ticket_status)
