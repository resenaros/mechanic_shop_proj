from app.extensions import ma
from app.models import Ticket

class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        include_fk = True  # Include foreign keys in the schema

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
