from app.extensions import ma
from app.models import Customer
from marshmallow import Schema, fields

# Schemas
# Define the schemas for serialization and deserialization
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

# Login schema: Only email and password, with validation
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

login_schema = LoginSchema()