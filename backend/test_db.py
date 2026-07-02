import os

from flask import jsonify

from app import create_app, db
from app.services.db import find_all, find_one, insert_one, delete_one, update_one, query_result_to_dict, query_results_to_dict
from app.models import Player, Game, Match, Player_to_Match, Match_to_Game, Game_to_player, Wishlist

app = create_app()

with app.app_context():

    updt = update_one("games", {'bgg_id' : 1}, {'belongs_to_user': None})

    print(f"update game: {updt}")

    dele = delete_one("players", {'username': 'Alxr'})

    print(f"delete player : {dele}")

    pl = {
        'username': 'Alxr',
        'password': hash('azerty'),
        'email': None,
        'image': '',
        # 'created_at' : '',
        'total_matches': 0,
        'wins': 0,
        'winstreak': 0,
        'longest_winstreak': 0,
    }

    ins = insert_one("players", pl)

    print(f"insert player ins : {ins.id}")
    print(f"insert player pl : {pl}")


    players = find_all("players", {})
    print(f"len(players) = {len(players)}")
    for player in players:
        print(f"Player ID: {player.id}, Username: {player.username}, Email: {player.email}")
        print(f"Player result: {player}")
        playerDict = player.__dict__
        print(f"Player dict: {playerDict}")
        playerDictwo_sa = playerDict.copy()
        del playerDictwo_sa['_sa_instance_state']
        print(f"Player dict: {playerDictwo_sa}")
        jsonRet = jsonify(playerDictwo_sa)
        print(f"Player JSON: {jsonRet.get_json()}")
    
    print("\n\n\n")

    player = find_one("players", {'username': 'Alxr'})

    print(f"Player result: {player}")
    playerDict = player.__dict__
    print(f"Player dict: {playerDict}")
    playerDictwo_sa = playerDict.copy()
    del playerDictwo_sa['_sa_instance_state']
    print(f"Player dict: {playerDictwo_sa}")
    jsonRet = jsonify(playerDictwo_sa)
    print(f"Player JSON: {jsonRet.get_json()}")

    print("\n\n\n")

    # insert_one("matches", {
    #     game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    #     date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    #     duration = db.Column(db.Integer)  # Duration in minutes
    #     nb_players = db.Column(db.Integer)
    #     nb_teams = db.Column(db.Integer, default=0)
    #     winning_team = db.Column(db.Integer, default=None)
    #     winning_score = db.Column(db.Integer, default=None)
    #     is_cooperative = db.Column(db.Boolean, default=False)
    #     is_over = db.Column(db.Boolean, default=True) # Indicates if the match is over or still ongoing
    #     note = db.Column(db.String(1024))
    # })

    matches_per_player_nb = db.session.query(Player, Match, Player_to_Match
    ).filter(Player.username == 'Alxr'
    ).join(Player_to_Match, Player.id==Player_to_Match.player_id
    ).join(Match, Player_to_Match.match_id==Match.id
    ).count()
    print(f"Matches for player 'Alxr': {matches_per_player_nb}")

    matches_per_player = db.session.query(Player, Match, Player_to_Match
    ).filter(Player.username == 'Alxr'
    ).join(Player_to_Match, Player.id==Player_to_Match.player_id
    ).join(Match, Player_to_Match.match_id==Match.id
    ).all()
    for match in matches_per_player:
        print(f"Match result: {match}")
        matchDict = match.__dict__
        print(f"Match dict: {matchDict}")
        matchDictwo_sa = matchDict.copy()
        del matchDictwo_sa['_sa_instance_state']
        print(f"Match dict: {matchDictwo_sa}")
        jsonRet = jsonify(matchDictwo_sa)
        print(f"Match JSON: {jsonRet.get_json()}")

    jwt_storage = os.getenv('JWT_STORAGE', 'cookie')
    print(f"JWT_STORAGE: {jwt_storage}")


    game_data = {
        'bgg_id': '1',
        'name': 'Azul',
        'base_game_id': None,  # For expansions, store the base game ID, None for base games
        'min_players': 2,
        'max_players': 4,
        'avg_duration': 60,
        'year_published': '',
        'image': 'azul.jpg',
        'is_cooperative': False,
        'is_team_based': False,
        'description': 'Azul is a tile-placement game.',
        'rulebook': None,
        'scoring_sheet': None
    }

    if find_one("games", {'bgg_id': '1'}) is None:
        ins = insert_one("games", game_data)
        print(f"insert game : {ins}")
    else:
        print(f"Game with bgg_id '1' is : {query_result_to_dict(find_one('games', {'bgg_id': '1'}))}")

    # results = db.session.query(Player, Match, Player_to_Match, Game, Match_to_Game
    #     ).filter(Player.username == "Alxr"
    #     ).join(Player_to_Match, Player.id==Player_to_Match.player_id
    #     ).filter(Player_to_Match.win == True
    #     ).join(Match, Player_to_Match.match_id==Match.id
    #     ).join(Match_to_Game, Match.id==Match_to_Game.match_id
    #     ).join(Game, Match_to_Game.game_id==Game.id
    #     ).order_by(Match.date.desc()
    #     ).group_by(Match.id
    #     ).all()
    
    results = Player.query.join(Player_to_Match, Player.id==Player_to_Match.player_id
        ).join(Match, Player_to_Match.match_id==Match.id
        ).join(Match_to_Game, Match.id==Match_to_Game.match_id
        ).join(Game, Match_to_Game.game_id==Game.id
        ).filter(Player.username=="Alxr", Player_to_Match.win==True
        ).all()

    print(f"Results : {results}")