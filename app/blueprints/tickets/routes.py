from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Ticket, Mechanic
from .schemas import ticket_schema, tickets_schema
from app.blueprints.mechanics.schemas import mechanics_schema  # <-- import here
from . import tickets_bp
from app.extensions import cache, limiter

# POST '/' - Create ticket
@tickets_bp.route('/', methods=['POST'])
def create_ticket():
    """
    Create a new service ticket.
    Expected JSON:
    {
        "vin": "string",
        "ticket_date": "YYYY-MM-DD",
        "customer_id": int
    }
    """
    try:
        ticket_data = ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_ticket = Ticket(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return ticket_schema.jsonify(new_ticket), 201

# GET '/' - Get all tickets
@tickets_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds
def get_tickets():
    query = select(Ticket)
    tickets = db.session.execute(query).scalars().all()
    return tickets_schema.jsonify(tickets), 200

# GET '/<ticket_id>/mechanics' - Get all mechanics for a specific ticket
@tickets_bp.route('/<int:ticket_id>/mechanics', methods=['GET'])
@cache.cached(timeout=60)  # Cache the response for 60 seconds
def get_ticket_mechanics(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404

    return mechanics_schema.jsonify(ticket.mechanics), 200

# PUT '/<ticket_id>/assign-mechanic/<mechanic_id>' - Assign mechanic to ticket
@tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()
    return ticket_schema.jsonify(ticket), 200

# PUT '/<ticket_id>/remove-mechanic/<mechanic_id>' - Remove mechanic from ticket
@tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()
        return jsonify({"message": f"Successfully removed mechanic {mechanic_id}: {mechanic.name} from ticket {ticket_id}."}), 200
    else:
        return jsonify({"error": f"Mechanic {mechanic_id}: {mechanic.name} is not assigned to ticket {ticket_id}."}), 404

# PATCH '/<ticket_id>' - Partially update a ticket
@tickets_bp.route('/<int:ticket_id>', methods=['PATCH'])
@limiter.limit("5 per day")  # Rate limit to 5 requests per day
def patch_ticket(ticket_id):
    """
    Partially update a ticket. Only fields provided in the request will be updated.
    Example JSON:
    {
        "vin": "new vin",
        "ticket_date": "YYYY-MM-DD"
    }
    """
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found."}), 404

    if not request.json:
        return jsonify({"error": "No data provided."}), 400

    try:
        ticket_data = ticket_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    updated = False
    for key, value in ticket_data.items():
        if hasattr(ticket, key):
            setattr(ticket, key, value)
            updated = True

    if not updated:
        return jsonify({"error": "No valid fields provided for update."}), 400

    db.session.commit()
    return ticket_schema.jsonify(ticket), 200