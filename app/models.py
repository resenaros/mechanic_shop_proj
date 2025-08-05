from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from datetime import date
from typing import List


# Create a base class for our models
class Base(DeclarativeBase):
    pass
 
# Instantiate your SQLAlchemy database
db = SQLAlchemy(model_class=Base)


# Define the models

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    tickets: Mapped[List['Ticket']] = db.relationship(back_populates='customer') #New relationship attribute

ticket_mechanic = db.Table(
    'ticket_mechanic',
    Base.metadata,
    db.Column('ticket_id', db.ForeignKey('tickets.id')),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'))
)

class Ticket(Base):
    __tablename__ = 'tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(255), nullable=False)
    ticket_date: Mapped[date] = mapped_column(db.Date)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))

    customer: Mapped['Customer'] = db.relationship(back_populates='tickets')
    mechanics: Mapped[List['Mechanic']] = db.relationship(secondary=ticket_mechanic, back_populates='tickets')

     # --- Inventory Relationship ---
    parts: Mapped[List['Inventory']] = db.relationship(
        'Inventory',
        secondary='ticket_inventory',
        back_populates='tickets'
    )
    
class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    
    tickets: Mapped[List['Ticket']] = db.relationship(secondary=ticket_mechanic, back_populates='mechanics')

# --- Inventory Many-to-Many Junction Table (with quantity field) ---
# This table links tickets and inventory parts, and tracks how many of each part is used in a ticket.
class TicketInventory(Base):
    __tablename__ = 'ticket_inventory'
    ticket_id: Mapped[int] = mapped_column(db.ForeignKey('tickets.id'), primary_key=True)
    inventory_id: Mapped[int] = mapped_column(db.ForeignKey('inventory.id'), primary_key=True)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False, default=1)

# --- Inventory Model ---
class Inventory(Base):
    __tablename__ = 'inventory'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    # Relationship to tickets through the junction table
    tickets: Mapped[List['Ticket']] = db.relationship(
        'Ticket',
        secondary='ticket_inventory',
        back_populates='parts'
    )
