import os
from app.models import db
from app import create_app

# NOTE: SAFE to remove
# config_name = os.getenv('FLASK_CONFIG', 'DevelopmentConfig') # check env file----THIS WAS ADDED

# Create the Flask application
app = create_app('ProductionConfig')

# MARK: Welcome message at the root 
@app.route('/')
def index():
    return "Welcome to the Mechanic Shop API. See api/docs/ for documentation."

# MARK: 
# ? REVIEW: Unsure if this should be kept during the production phase
# Create the table
with app.app_context():
    # db.drop_all()  # Drop all tables if they exist
    db.create_all()

# Run the application
# MARK:
# NOTE: app.run() is present but safely wrapped in if __name__ == "__main__": (so it’s ignored in production).
if __name__ == "__main__":
    app.run(debug=True)  # Set debug=True for development, or remove for production