from .schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import db, Customer
from . import customers_bp
from app.extensions import cache, limiter
from app.utils.util import encode_token, token_required

# Login Route
# This route allows a customer to log in using their email and password.
@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        username = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify({'messages': e.messages}), 400

    query = select(Customer).where(Customer.email == username)
    customer = db.session.execute(query).scalar_one_or_none() #Query customer table for a customer with this email

    if customer and customer.password == password: #if we have a customer associated with the username, validate the password
        auth_token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401


# Customer Routes
# Create a customer
@customers_bp.route('/', methods=['POST'])
@limiter.limit("5 per day")  # Rate limit to 5 requests per day
def create_customer():     
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data['email']) #Checking our db for a customer with this email
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Email already associated with an account."}), 400

    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

#GET ALL customers
@customers_bp.route("/", methods=['GET'])
def get_customers():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page, error_out=False).items
        return customers_schema.jsonify(customers), 200
    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(customers)

#GET SPECIFIC customer
@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404

#UPDATE SPECIFIC customer
@customers_bp.route("/", methods=['PUT'])
@token_required
@limiter.limit("10 per day")  # Rate limit to 10 requests per day
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

#PATCH SPECIFIC customer
@customers_bp.route("/", methods=['PATCH'])
@token_required
@limiter.limit("5 per day")  # Rate limit to 5 requests per day
def patch_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        customer_data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

#DELETE SPECIFIC customer
@customers_bp.route("/", methods=['DELETE'])
@token_required
@limiter.limit("5 per day")  # Rate limit to 5 requests per day
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {customer_id}, successfully deleted.'}), 200
