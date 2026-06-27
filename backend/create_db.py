from app import create_app, db

app = create_app()

with app.app_context():
    db.drop_all()  # Drop all existing tables
    db.create_all() # Create new tables based on the models defined in app/models.py