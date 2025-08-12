# app/utils/util.py
from datetime import datetime, timedelta, timezone
from jose import jwt
import jose
from flask import request, jsonify
from functools import wraps

SECRET_KEY = "a super secret, secret key"

def encode_token(customer_id): #using unique pieces of info to make our tokens customer specific
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0,hours=1), #Setting the expiration time to an hour past now
        'iat': datetime.now(timezone.utc), #Issued at
        'sub':  str(customer_id), #This needs to be a string or the token will be malformed and won't be able to be decoded.
        'role': 'customer'  # Adding a role for future use
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Look for the token in the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            if data.get('role') != 'customer':
                return jsonify({'message': 'Invalid token role!'}), 403
            customer_id = data['sub']  # Fetch the customer ID

        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401

        kwargs['token_customer_id'] = customer_id  # Pass the customer ID to the route
        return f(*args, **kwargs)

    return decorated

# Mechanic Token Functions

def encode_mechanic_token(mechanic_id):
    """
    Encode a JWT token for a mechanic.
    Payload includes mechanic_id as 'sub' and role as 'mechanic'.
    """
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(mechanic_id),
        'role': 'mechanic'  # Explicitly mark role
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def mechanic_token_required(f):
    """
    Decorator to protect routes for mechanics.
    Validates the token and passes mechanic_id to the route.
    Only allows access if role in token is 'mechanic'.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Only allow tokens with role "mechanic"
            if data.get('role') != 'mechanic':
                return jsonify({'message': 'Mechanic authorization required!'}), 403
            mechanic_id = data['sub']

        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401

        kwargs['token_mechanic_id'] = mechanic_id  # Pass the mechanic ID to the route
        return f(*args, **kwargs)

    return decorated