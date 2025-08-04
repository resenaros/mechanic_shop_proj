from app.extensions import ma
from app.models import Inventory, TicketInventory
from marshmallow import fields

# Auto-generates schema from Inventory model
class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)

# TicketInventorySchema for showing quantity if needed
class TicketInventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TicketInventory

ticket_inventory_schema = TicketInventorySchema()
ticket_inventories_schema = TicketInventorySchema(many=True)