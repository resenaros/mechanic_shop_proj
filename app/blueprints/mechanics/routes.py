from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Mechanic
from .schemas import mechanic_schema, mechanics_schema
from . import mechanics_bp
from app.extensions import cache, limiter

# POST '/' : Creates a new Mechanic
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("5/ day")  # Rate limit to 5 requests per day
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Ensure unique email
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing = db.session.execute(query).scalars().all()
    if existing:
        return jsonify({"error": "Email already in use."}), 400

    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

# GET '/': Retrieves all Mechanics
@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page, error_out=False).items
        return mechanics_schema.jsonify(mechanics), 200
    except:
        query = select(Mechanic)
        mechanics = db.session.execute(query).scalars().all()
        return mechanics_schema.jsonify(mechanics)

# GET '/<int:id>': Retrieve a single mechanic
@mechanics_bp.route('/<int:id>', methods=['GET'])
def get_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    return mechanic_schema.jsonify(mechanic)

# PUT '/<int:id>': Updates a specific Mechanic
@mechanics_bp.route('/<int:id>', methods=['PUT'])
@limiter.limit("10 per day")  # Rate limit to 10 requests per day
def update_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

# PATCH '/<int:id>': Partially updates a specific Mechanic
@mechanics_bp.route('/<int:id>', methods=['PATCH'])
@limiter.limit("5 per day")  # Rate limit to 5 requests per day
def patch_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

# DELETE '/<int:id>': Deletes a specific Mechanic
@mechanics_bp.route('/<int:id>', methods=['DELETE'])
@limiter.limit("5 per day")  # Rate limit to 5 requests per day
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic id: {id}, successfully deleted."})

# GET '/popular' - Get popular mechanics
@mechanics_bp.route('/popular', methods=['GET'])
def popular_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key=lambda mechanic: len(mechanic.tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics), 200

# GET '/search' - Search for mechanics by name
@mechanics_bp.route('/search', methods=['GET'])
def search_mechanic():
    name = request.args.get('name')

    query = select(Mechanic).where(Mechanic.name.like(f"%{name}%"))
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics)