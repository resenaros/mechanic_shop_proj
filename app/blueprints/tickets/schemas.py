from marshmallow import fields
from app.extensions import ma
from app.models import Ticket

class TicketSchema(ma.SQLAlchemyAutoSchema):
    customers = fields.Nested('CustomerSchema')
    mechanics = fields.Nested('MechanicSchema', many=True)
    class Meta:
        model = Ticket
        include_fk = True  # Include foreign keys in the schema
        
class EditTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
edit_ticket_schema = EditTicketSchema()

