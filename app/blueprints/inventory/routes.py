from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Inventory, TicketInventory
from .schemas import inventory_schema, inventories_schema
from . import inventory_bp
from app.extensions import limiter

# --- CRUD Routes for Inventory ---

# Create a new inventory part
@inventory_bp.route('/', methods=['POST'])
@limiter.limit("10 per day")
def create_inventory():
    try:
        part_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_part = Inventory(**part_data)
    db.session.add(new_part)
    db.session.commit()
    return inventory_schema.jsonify(new_part), 201

# Get all parts
@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    query = select(Inventory)
    parts = db.session.execute(query).scalars().all()
    return inventories_schema.jsonify(parts), 200

# Get a specific part
@inventory_bp.route('/<int:part_id>', methods=['GET'])
def get_inventory_part(part_id):
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"error": "Part not found."}), 404
    return inventory_schema.jsonify(part), 200

# Update a part
@inventory_bp.route('/<int:part_id>', methods=['PUT'])
@limiter.limit("10 per day")
def update_inventory(part_id):
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"error": "Part not found."}), 404
    try:
        part_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    for key, value in part_data.items():
        setattr(part, key, value)
    db.session.commit()
    return inventory_schema.jsonify(part), 200

# Delete a part
@inventory_bp.route('/<int:part_id>', methods=['DELETE'])
@limiter.limit("5 per day")
def delete_inventory(part_id):
    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"error": "Part not found."}), 404
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f"Part id {part_id} deleted"}), 200

