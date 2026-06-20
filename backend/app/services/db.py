# MONGO_DEL from pymongo import MongoClient
from datetime import datetime
from app import db
from app.models import Player, Game, Match, Wishlist, Achievement, Rulebook
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import JSONB
import os

load_dotenv()

# MONGO_DEL MongoDB connection
# MONGO_DEL MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')

# MONGO_DEL Connectron to MongoDB
# MONGO_DEL client = MongoClient(MONGO_URI)
# MONGO_DEL db = client[DB_NAME]

# MONGO_DEL Collections
# MONGO_DEL games_collection = db["games"]
# MONGO_DEL matches_collection = db["matches"]
# MONGO_DEL players_collection = db["players"]
# MONGO_DEL wishlists_collection = db["wishlists"]
# MONGO_DEL achievements_collection = db["achievements"]
# MONGO_DEL rulebooks_collection = db["rulebooks"]

def find_one(collection, query):
    """Find a single document in the specified collection."""
    if collection == "players":
        return Player.query.filter_by(**query).first()
    elif collection == "games":
        return Game.query.filter_by(**query).first()
    elif collection == "matches":
        return Match.query.filter_by(**query).first()
    elif collection == "wishlists":
        return Wishlist.query.filter_by(**query).first()
    elif collection == "achievements":
        return Achievement.query.filter_by(**query).first()
    elif collection == "rulebooks":
        return Rulebook.query.filter_by(**query).first()
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
    elif collection == "wishlists":
        return Wishlist.query.filter_by(**query).all()
    elif collection == "achievements":
        return Achievement.query.filter_by(**query).all()
    elif collection == "rulebooks":
        return Rulebook.query.filter_by(**query).all()
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
    elif collection == "wishlists":
        return Wishlist.query.filter_by(**query).count()
    elif collection == "achievements":
        return Achievement.query.filter_by(**query).count()
    elif collection == "rulebooks":
        return Rulebook.query.filter_by(**query).count()
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
    elif collection == "wishlists":
        wishlist = Wishlist(**document)
        db.session.add(wishlist)
    elif collection == "achievements":
        achievement = Achievement(**document)
        db.session.add(achievement)
    elif collection == "rulebooks":
        rulebook = Rulebook(**document)
        db.session.add(rulebook)
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
    elif collection == "wishlists":
        wishlist = Wishlist.query.filter_by(**query).first()
        if wishlist:
            for key, value in update.items():
                setattr(wishlist, key, value)
    elif collection == "achievements":
        achievement = Achievement.query.filter_by(**query).first()
        if achievement:
            for key, value in update.items():
                setattr(achievement, key, value)
    elif collection == "rulebooks":
        rulebook = Rulebook.query.filter_by(**query).first()
        if rulebook:
            for key, value in update.items():
                setattr(rulebook, key, value)
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
    elif collection == "wishlists":
        wishlist = Wishlist.query.filter_by(**query).first()
        if wishlist:
            db.session.delete(wishlist)
    elif collection == "achievements":
        achievement = Achievement.query.filter_by(**query).first()
        if achievement:
            db.session.delete(achievement)
    elif collection == "rulebooks":
        rulebook = Rulebook.query.filter_by(**query).first()
        if rulebook:
            db.session.delete(rulebook)
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
    elif collection == "wishlists":
        wishlists = Wishlist.query.filter_by(**query).all()
        for wishlist in wishlists:
            db.session.delete(wishlist)
    elif collection == "achievements":
        achievements = Achievement.query.filter_by(**query).all()
        for achievement in achievements:
            db.session.delete(achievement)
    elif collection == "rulebooks":
        rulebooks = Rulebook.query.filter_by(**query).all()
        for rulebook in rulebooks:
            db.session.delete(rulebook)
    else:
        raise ValueError(f"Unknown collection: {collection}")
    
    db.session.commit()
