from datetime import datetime, timezone
from app import db
from sqlalchemy.dialects.postgresql import JSONB

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), default=None)
    image = db.Column(db.String(512), default='')
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    total_matches = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    winstreak = db.Column(db.Integer, default=0)
    longest_winstreak = db.Column(db.Integer, default=0)

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    bgg_id = db.Column(db.Integer, default=None)
    name = db.Column(db.String(512))
    base_game_id = db.Column(db.Integer, default=None)  # For expansions, store the base game ID, None for base games
    min_players = db.Column(db.Integer)
    max_players = db.Column(db.Integer)
    avg_duration = db.Column(db.Integer)
    year_published = db.Column(db.String(4))  # Year of publication, stored as a string to accommodate various formats
    image = db.Column(JSONB, default=dict)  # Store both URL and thumbnail
    is_cooperative = db.Column(db.Boolean, default=False)
    is_team_based = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(2048))
    belongs_to_user = db.Column(db.Integer, db.ForeignKey('players.id'), default=None)  # User ID of the possessor of the game, if applicable
    location = db.Column(db.String(256))
    rulebook = db.Column(db.String(512))  # URL or path to the rulebook
    scoring_sheet = db.Column(db.String(512))  # URL or path to the scoring sheet

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    duration = db.Column(db.Integer, default=None)  # Duration in minutes
    nb_players = db.Column(db.Integer)
    nb_teams = db.Column(db.Integer, default=0)
    winner = db.Column(db.Integer, default=None) # Either team id if nb_team > 0 or player_id
    winning_score = db.Column(db.Integer, default=None)
    is_cooperative = db.Column(db.Boolean, default=False)
    is_over = db.Column(db.Boolean, default=True) # Indicates if the match is over or still ongoing
    note = db.Column(db.String(1024))

class Player_to_Match(db.Model):
    __tablename__ = 'player_to_match'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    team_id = db.Column(db.Integer, default=None)
    score = db.Column(db.Integer, default=0)
    win = db.Column(db.Boolean, default=False)

class Match_to_Game(db.Model):
    __tablename__ = 'match_to_game'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))

