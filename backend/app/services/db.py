from app import db
from app.models import Player, Game, Match, Player_to_Match, Match_to_Game #, Wishlist, Achievement, Rulebook
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
    elif collection == "players_to_matches":
        return Player_to_Match.query.filter_by(**query).first()
    elif collection == "matches_to_games":
        return Match_to_Game.query.filter_by(**query).first()
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
    elif collection == "players_to_matches":
        return Player_to_Match.query.filter_by(**query).all()
    elif collection == "matches_to_games":
        return Match_to_Game.query.filter_by(**query).all()
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
    elif collection == "players_to_matches":
        return Player_to_Match.query.filter_by(**query).count()
    elif collection == "matches_to_games":
        return Match_to_Game.query.filter_by(**query).count()
    else:
        raise ValueError(f"Unknown collection: {collection}")

def insert_one(collection, document):
    """Insert a single document into the specified collection."""
    if collection == "players":
        ret = Player(**document)
        db.session.add(ret)
    elif collection == "games":
        ret = Game(**document)
        db.session.add(ret)
    elif collection == "matches":
        ret = Match(**document)
        db.session.add(ret)
    elif collection == "players_to_matches":
        ret = Player_to_Match(**document)
        db.session.add(ret)
    elif collection == "matches_to_games":
        ret = Match_to_Game(**document)
        db.session.add(ret)
    else:
        raise ValueError(f"Unknown collection: {collection}")
    
    db.session.commit()
    return ret

def update_one(collection, query, update):
    """Update a single document in the specified collection."""
    if collection == "players":
        ret = Player.query.filter_by(**query).first()
    elif collection == "games":
        ret = Game.query.filter_by(**query).first()
    elif collection == "matches":
        ret = Match.query.filter_by(**query).first()
    elif collection == "players_to_matches":
        ret = Player_to_Match.query.filter_by(**query).first()
    elif collection == "matches_to_games":
        ret = Match_to_Game.query.filter_by(**query).first()
    else:
        raise ValueError(f"Unknown collection: {collection}")
    
    if ret:
        for key, value in update.items():
            setattr(ret, key, value)
    db.session.commit()
    return ret

def delete_one(collection, query):
    """Delete a single document from the specified collection."""
    if collection == "players":
        ret = Player.query.filter_by(**query).first()
        if ret:
            db.session.delete(ret)
    elif collection == "games":
        ret = Game.query.filter_by(**query).first()
        if ret:
            db.session.delete(ret)
    elif collection == "matches":
        ret = Match.query.filter_by(**query).first()
        if ret:
            db.session.delete(ret)
    elif collection == "players_to_matches":
        ret = Player_to_Match.query.filter_by(**query).first()
        if ret:
            db.session.delete(ret)
    elif collection == "matches_to_games":
        ret = Match_to_Game.query.filter_by(**query).first()
        if ret:
            db.session.delete(ret)
    else:
        raise ValueError(f"Unknown collection: {collection}")
    
    db.session.commit()

def delete_many(collection, query):
    """Delete multiple documents from the specified collection."""
    if collection == "players":
        rets = Player.query.filter_by(**query).all()
        for ret in rets:
            db.session.delete(ret)
    elif collection == "games":
        rets = Game.query.filter_by(**query).all()
        for ret in rets:
            db.session.delete(ret)
    elif collection == "matches":
        rets = Match.query.filter_by(**query).all()
        for ret in rets:
            db.session.delete(ret)
    elif collection == "players_to_matches":
        rets = Player_to_Match.query.filter_by(**query).all()
        for ret in rets:
            db.session.delete(ret)
    elif collection == "matches_to_games":
        rets = Match_to_Game.query.filter_by(**query).all()
        for ret in rets:
            db.session.delete(ret)
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