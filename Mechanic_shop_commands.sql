-- Mechanic Shop Commands SQL
-- This script creates the mechanic shop database and its tables, and provides commands to interact with the database.

-- Create  Database
CREATE DATABASE mechanic_shop;

-- Use the Database
USE mechanic_shop;

-- Show all tables
SHOW TABLES;

-- describe the customers table
DESCRIBE customers;

-- describe the mechanics table
DESCRIBE mechanics;

-- describe the tickets table
DESCRIBE tickets;

-- describe the ticket_mechanic junction table
DESCRIBE ticket_mechanic;

-- show all data in the customers table
SELECT * FROM customers;

-- show all data in the mechanics table
SELECT * FROM mechanics;

-- show all data in the tickets table
SELECT * FROM tickets;

-- show all data in the ticket_mechanic junction table
SELECT * FROM ticket_mechanic;