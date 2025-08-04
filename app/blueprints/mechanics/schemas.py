from marshmallow import Schema, fields
from app.extensions import ma
from app.models import Mechanic

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

class MechanicLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

mechanic_login_schema = MechanicLoginSchema()