# Mechanic Shop API

This project is a RESTful API for managing service tickets in a mechanic shop. It allows for the creation, updating, and management of service tickets, customers, and mechanics, including the assignment and removal of mechanics from tickets.

## Technologies Used

- **Python 3**
- **Flask** (web framework)
- **SQLAlchemy** (ORM for database models and relationships)
- **Marshmallow** (for serialization and validation)
- **MySQL** (relational database)

## Main Features

- **CRUD Operations**: Create, retrieve/read, update, and delete service tickets.
- **Assign and remove mechanics from tickets**
- **Retrieve all mechanics assigned to a given ticket**
- **Robust validation and error handling**

## Example API Endpoints

| Method | Endpoint                                             | Description                             |
| ------ | ---------------------------------------------------- | --------------------------------------- |
| POST   | `/tickets/`                                          | Create a new service ticket             |
| GET    | `/tickets/`                                          | Get all tickets                         |
| PATCH  | `/tickets/{ticket_id}`                               | Partially update a ticket               |
| PUT    | `/tickets/{ticket_id}/assign-mechanic/{mechanic_id}` | Assign a mechanic to a ticket           |
| PUT    | `/tickets/{ticket_id}/remove-mechanic/{mechanic_id}` | Remove a mechanic from a ticket         |
| GET    | `/tickets/{ticket_id}/mechanics`                     | Get all mechanics for a specific ticket |

## Learnings

- **Database Relationships:** Gained hands-on experience with SQLAlchemy's many-to-many relationships, junction tables, and how to manage them in an API context.
- **Serialization and Validation:** Learned how to use Marshmallow for input validation and output serialization, especially when dealing with foreign keys and nested data.
- **RESTful Design:** Developed a clear, consistent API with logical routes and status codes, making the backend easy to integrate with tools like Postman.
- **Error Handling:** Implemented robust error and validation messages, ensuring clients receive helpful feedback for invalid requests.
- **Separation of Concerns:** Maintained clean project structure by separating models, schemas, and routes.

## Database Navigation

A **SQL statement sheet** is provided in this repository to help you navigate and query the MySQL database using MySQL Workbench. Use it to:

- View, insert, or update records directly in the database
- Debug or inspect relationships and table contents during development

## How to Run

1. **Install dependencies:**  
   `pip install -r requirements.txt`

2. **Set up the MySQL database** (create the database and update your config).

3. **Run the Flask app:**  
   `flask run`

4. **Test endpoints using Postman** with the recommended collection naming conventions.

---
