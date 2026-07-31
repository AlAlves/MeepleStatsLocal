from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, decode_token
from jwt.exceptions import InvalidTokenError
from werkzeug.security import generate_password_hash, check_password_hash

from app.services.db import find_one, find_all, insert_one, update_one, delete_one, query_result_to_dict, query_results_to_dict, get_match_history, get_match_history_by_games, get_match_history_by_players, get_match_history_by_players_and_games, get_wins_per_player 


players_bp = Blueprint('users', __name__)

@players_bp.route('/get_players', methods=['GET'])
def get_players():
    """Get all players.

    Request: GET

    Returns:
        JSON: 
            'players' (list[dict<Model.Player>])
            or
            'error' (str)

    """
    try:
        players = find_all("players", {})
        players_data = query_results_to_dict(players)

        return jsonify(players_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
