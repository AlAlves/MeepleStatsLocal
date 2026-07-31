from datetime import datetime, time, timedelta, timezone

from flask import Blueprint, jsonify, render_template, request
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash


from app.services.db import find_one, find_all, insert_one, update_one, delete_one, query_result_to_dict, query_results_to_dict, get_match_history, get_match_history_by_games, get_match_history_by_players, get_match_history_by_players_and_games, get_wins_per_player


matches_bp = Blueprint('matches', __name__)

@matches_bp.route('/add_match', methods=['POST'])
@jwt_required()
def add_match():
    """Log a match.

    Request: POST
        games (list[dict]): List of games in the match (count expansions) with id (int)
        is_cooperative (bool): true if game is coop
        is_coop_win (bool): true if coop game was a win for players
        is_team_based (bool): true if the game is team based
        players (list[dict]): List of players in the match with score (int), username (str) and team (int, optionnal)
        date (str, optionnal): date of the match
        duration (str, optionnal): duration of the game
        is_over (str, optionnal): true if the game is over
        note (str, optionnal): optionnal notes

    Returns:
        JSON: Either response or error description containing
            'message' (str)
            'match_id' (int)
            'match_to_game_id' (int)
            'players_to_match_id_tab' (int)
            or
            'error' (str)

    """

    # PARSE GAME DATA (multiple if extensions)
    game_ids_is_expansion = [] # list of tuple (id, bool, id) with id_of_game, is_expansion, id_of_base_game (if expansion, else None)
    main_game_id = None
    index = 0
    while True:
        game_id = request.form.get(f'games[{index}][id]') or None
        if game_id is None:
            break
        game = find_one("games", {'id': game_id})
        if not game:
            return jsonify({'error': f"Game {game_id} not found"}), 404
        game_id_is_expansion = (game_id, game.base_game_id is not None, game.base_game_id)
        game_ids_is_expansion.append(game_id_is_expansion)
        index += 1

    is_cooperative = request.form.get(f'is_cooperative')
    is_team_based = request.form.get(f'is_team_based')
    if is_cooperative:
        is_coop_win = request.form.get(f'is_coop_win')
    
    # Search for main_game_id and check for multiple base game
    main_game_id = None
    nb_games = len(game_ids_is_expansion)
    for game_id, is_expansion, base_game_id in game_ids_is_expansion:
        if not is_expansion:
            if main_game_id is None:
                main_game_id = game_id
            elif main_game_id == game_id:
                game_ids_is_expansion.remove( (game_id, is_expansion, base_game_id) ) # remove duplicated basegame
            else:
                return jsonify({'error': f"Multiple base games found in the match: {main_game_id}, {game_id}"}), 400
        else:
            if main_game_id is None or main_game_id == base_game_id:
                main_game_id = base_game_id
            else:
                return jsonify({'error': f"Multiple base games found in the match: {main_game_id}, {base_game_id}"}), 400

    # PARSE PLAYER DATA
    players = []
    teams = []
    winner_id = None
    best_score = None
    winning_team = None
    index = 0
    while True:
        player_id = request.form.get(f'players[{index}][id]') or None
        # Check if another player is defined, else break loop
        if player_id is None:
            break
        player_score = request.form.get(f'players[{index}][score]') or 0
        player_username = request.form.get(f'players[{index}][username]')
        player_team = 1 if is_cooperative else ( request.form.get(f'players[{index}][team]') or None )
        if best_score is None or player_score > best_score:
            winner_id = player_id
            best_score = player_score
            winning_team = player_team
        if player_team not in teams and player_team is not None:
            teams.append(player_team)
        
        players.append({'id': player_id, 'username': player_username, 'score': int(player_score), 'team': player_team})
        index += 1
    
    if is_cooperative:
        teams = [0, 1] # 0 is ENV, 1 is PLAYERS
        winning_team = 1 if is_coop_win else 0

    # MATCH DATA
    date_str = request.form.get('date')
    date_format = '%d/%m/%Y'
    
    match_data = {
        'date' : datetime.strptime(date_str, date_format) if date_str is not None else datetime.now(timezone.utc),
        'duration' : int(request.form.get('duration')) if request.form.get('duration') is not None else None,
        'nb_players' : len(players),
        'nb_teams' : len(teams) if is_team_based or is_cooperative else 0,
        'winner' : int(winning_team) if len(teams) > 0 or is_cooperative else int(winner_id),
        'best_score' : int(best_score),
        'is_cooperative' : game.is_cooperative,
        'is_over' : request.form.get('is_over', '').strip().lower() in ['true', '1', 'yes'] if request.form.get('is_over') is not None else True,
        'note' : request.form.get('note'),
    }

    new_match = insert_one("matches", match_data)
    match_id = new_match.id 

    # MATCH TO GAME INFO
    match_to_game_data = {
        'match_id' : match_id,
        'game_id' : base_game_id
    }

    m2g = insert_one("matches_to_games", match_to_game_data)
    m2gs = [m2g.id]

    for game_id, is_expansion, base_game_id in game_ids_is_expansion:
        match_to_game_data = {
            'match_id' : match_id,
            'game_id' : game_id
        }

        m2g = insert_one("matches_to_games", match_to_game_data)
        m2gs.append(m2g.id)


    # PLAYER TO MATCH INFO
    p2ms = []

    for player in players:
        player_to_match_data = {
            'player_id' : player['id'],
            'match_id' : match_id,
            'team_id' : player['team'],
            'score' : player['score'],
            'win' : player['team'] == winning_team if is_team_based or is_cooperative else player['score'] == best_score,
        }

        p2m = insert_one("players_to_matches", player_to_match_data)
        p2ms.append(p2m.id)
    
    ret = {
        'message': 'Match logged successfully',
        'match_id': match_id,
        'match_to_game_id': m2gs,
        'players_to_match_id_tab': p2ms,
    }

    return jsonify(ret), 201


@matches_bp.route('/get_matches', methods=['GET'])
@jwt_required()
def get_matches():
    """Get match history TODO

    Returns:
        _type_: _description_
    """
    # Get all the matches from the database
    try:
        index = 0
        players = []
        while True:
            player_id = request.form.get(f"players[{index}][id]") or None
            # Check if another player is defined, else break loop
            if player_id is None:
                break
            players.append(player_id)
            index += 1

        matches = []
        if not players:
            matches = get_match_history()
        else:
            matches = get_match_history_by_players(players)

        matches_data = []

        for match in matches:
            match_data = {
                'image_url': f"/uploads/matches/{match.image}" if match.image else None,
                'players' : players,
                'match' : query_result_to_dict(match),
            }

            matches_data.append(match_data)

        # Sort matches by date in descending order
        matches_data.sort(key=lambda x: (x['match']['date'], x['match']['id']), reverse=True)

        return jsonify(matches_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
