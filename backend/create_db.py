from app import create_app, db
from app.services.db import delete_many

app = create_app()

with app.app_context():
    # Delete all records
    delete = False
    if delete:
        delete_many("games_to_players", {})
        delete_many("matches_to_games", {})
        delete_many("players_to_matches", {})
        delete_many("matches", {})
        delete_many("games", {})
        delete_many("players", {})

    db.drop_all()  # Drop all existing tables
    db.create_all() # Create new tables based on the models defined in app/models.py