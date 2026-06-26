from app import db
from app.models import Player, Game, Match #, Wishlist, Achievement, Rulebook
from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.getenv('DB_NAME')


def find_one(collection, query):
    """Find a single document in the specified collection."""
    if collection == "players":
        return Player.query.filter_by(**query).first()
    elif collection == "games":
        return Game.query.filter_by(**query).first()
    elif collection == "matches":
        return Match.query.filter_by(**query).first()
    else:
        raise ValueError(f"Unknown collection: {collection}")

def find_all(collection, query):
    """Find all documents in the specified collection that match the query."""
    if collection == "players":
        return Player.query.filter_by(**query).all()
    elif collection == "games":
        return Game.query.filter_by(**query).all()
    elif collection == "matches":
        return Match.query.filter_by(**query).all()
    else:
        raise ValueError(f"Unknown collection: {collection}")

def count_documents(collection, query):
    """Count the number of documents in the specified collection that match the query."""
    if collection == "players":
        return Player.query.filter_by(**query).count()
    elif collection == "games":
        return Game.query.filter_by(**query).count()
    elif collection == "matches":
        return Match.query.filter_by(**query).count()
    else:
        raise ValueError(f"Unknown collection: {collection}")

def insert_one(collection, document):
    """Insert a single document into the specified collection."""
    if collection == "players":
        player = Player(**document)
        db.session.add(player)
    elif collection == "games":
        game = Game(**document)
        db.session.add(game)
    elif collection == "matches":
        match = Match(**document)
        db.session.add(match)
    else:
        raise ValueError(f"Unknown collection: {collection}")
    
    db.session.commit()

def update_one(collection, query, update):
    """Update a single document in the specified collection."""
    if collection == "players":
        player = Player.query.filter_by(**query).first()
        if player:
            for key, value in update.items():
                setattr(player, key, value)
    elif collection == "games":
        game = Game.query.filter_by(**query).first()
        if game:
            for key, value in update.items():
                setattr(game, key, value)
    elif collection == "matches":
        match = Match.query.filter_by(**query).first()
        if match:
            for key, value in update.items():
                setattr(match, key, value)
    else:
        raise ValueError(f"Unknown collection: {collection}")
    
    db.session.commit()

def delete_one(collection, query):
    """Delete a single document from the specified collection."""
    if collection == "players":
        player = Player.query.filter_by(**query).first()
        if player:
            db.session.delete(player)
    elif collection == "games":
        game = Game.query.filter_by(**query).first()
        if game:
            db.session.delete(game)
    elif collection == "matches":
        match = Match.query.filter_by(**query).first()
        if match:
            db.session.delete(match)
    else:
        raise ValueError(f"Unknown collection: {collection}")
    
    db.session.commit()

def delete_many(collection, query):
    """Delete multiple documents from the specified collection."""
    if collection == "players":
        players = Player.query.filter_by(**query).all()
        for player in players:
            db.session.delete(player)
    elif collection == "games":
        games = Game.query.filter_by(**query).all()
        for game in games:
            db.session.delete(game)
    elif collection == "matches":
        matches = Match.query.filter_by(**query).all()
        for match in matches:
            db.session.delete(match)
    else:
        raise ValueError(f"Unknown collection: {collection}")
    
    db.session.commit()

def query_result_to_dict(result):
    """Convert a single SQLAlchemy query result to a dictionary."""
    if not result:
        return None
    result_dict = result.__dict__.copy()
    if '_sa_instance_state' in result_dict:
            del result_dict['_sa_instance_state']
    return result_dict

def query_results_to_dict(results):
    """Convert a list of SQLAlchemy query results to a list of dictionaries."""
    return [query_result_to_dict(result) for result in results]