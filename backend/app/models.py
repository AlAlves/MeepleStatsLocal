from datetime import datetime, timezone
from app import db
from sqlalchemy.dialects.postgresql import JSONB

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), default=None)
    image = db.Column(db.String(512), default='') # URL or path to image
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    total_matches = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    winstreak = db.Column(db.Integer, default=0)
    longest_winstreak = db.Column(db.Integer, default=0)
    p2m = db.relationship("Player_to_Match", cascade="all, delete")
    g2p = db.relationship("Game_to_Player", cascade="all, delete")

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    bgg_id = db.Column(db.Integer, default=None)
    name = db.Column(db.String(512), unique=True, nullable=False)
    base_game_id = db.Column(db.Integer, default=None)  # For expansions, store the base game ID, None for base games
    min_players = db.Column(db.Integer)
    max_players = db.Column(db.Integer)
    avg_duration = db.Column(db.Integer)
    year_published = db.Column(db.String(4))  # Year of publication, stored as a string to accommodate various formats
    image = db.Column(db.String(512), default='') # URL or path to image
    is_cooperative = db.Column(db.Boolean, default=False)
    is_team_based = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(2048))
    rulebook = db.Column(db.String(512))  # URL or path to the rulebook
    scoring_sheet = db.Column(db.String(512))  # URL or path to the scoring sheet
    m2g = db.relationship("Match_to_Game", cascade="all, delete")
    g2p = db.relationship("Game_to_Player", cascade="all, delete")

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    duration = db.Column(db.Integer, default=None)  # Duration in minutes
    image = db.Column(db.String(512), default='') # URL or path to image
    nb_players = db.Column(db.Integer)
    nb_teams = db.Column(db.Integer, default=0)
    winner = db.Column(db.Integer, default=None) # Either team id if nb_team > 0 or player_id
    winning_score = db.Column(db.Integer, default=None)
    is_cooperative = db.Column(db.Boolean, default=False)
    is_over = db.Column(db.Boolean, default=True) # Indicates if the match is over or still ongoing
    note = db.Column(db.String(1024))
    p2m = db.relationship("Player_to_Match", cascade="all, delete")
    m2g = db.relationship("Match_to_Game", cascade="all, delete")

class Player_to_Match(db.Model):
    __tablename__ = 'players_to_matches'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    team_id = db.Column(db.Integer, default=None)
    score = db.Column(db.Integer, default=0)
    win = db.Column(db.Boolean, default=False)

class Match_to_Game(db.Model):
    __tablename__ = 'matches_to_games'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

class Game_to_Player(db.Model): # Who possesses which game
    __tablename__ = 'games_to_players'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    favorite = db.Column(db.Boolean, default=False)
    wishlisted = db.Column(db.Boolean, default=False)
    owned = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(256))

