import os
from app.models import db
from app import create_app

# config_name = os.getenv('FLASK_CONFIG', 'DevelopmentConfig') # check env file----THIS WAS ADDED
# Create the Flask application
app = create_app('ProductionConfig')

# Create the table
with app.app_context():
    # db.drop_all()  # Drop all tables if they exist
    db.create_all()

# Run the application
if __name__ == "__main__":
    app.run(debug=True)  # Set debug=True for development, or remove for production