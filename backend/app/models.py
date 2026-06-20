from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSONB

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256))
    image = db.Column(db.String(512), default='')
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    achievements = db.Column(JSONB, default=list)
    wins = db.Column(db.Integer, default=0)
    winstreak = db.Column(db.Integer, default=0)
    longest_winstreak = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    total_matches = db.Column(db.Integer, default=0)
    num_competitive_win = db.Column(db.Integer, default=0)

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    bgg_id = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(512))
    isGifted = db.Column(db.Boolean, default=False)
    price = db.Column(db.Numeric)
    location = db.Column(db.String(256))
    data = db.Column(JSONB, default=dict)

class Player_to_Match(db.Model):
    __tablename__ = 'player_to_match'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    win = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    in_team = db.Column(db.Boolean, default=False)
    team = db.Column(db.Integer, default=0)
    coop = db.Column(db.Boolean, default=False)

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    game_name = db.Column(db.String(512))
    game_image = db.Column(db.String(512))
    date = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    expansion = db.Column(db.Array(db.String(256)))
    note = db.Column(db.String(1024))
    use_manual_winner = db.Column(db.String(256))
    data = db.Column(JSONB, default=dict)

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(128), nullable=False)
    data = db.Column(JSONB, default=dict)

class Rulebook(db.Model):
    __tablename__ = 'rulebooks'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(JSONB, default=dict)

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(JSONB, default=dict)