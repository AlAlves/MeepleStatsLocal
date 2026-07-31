from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity

import os
import uuid
from flask import current_app
import requests
import json

from app.services.db import find_one, find_all, insert_one, update_one, delete_one, query_result_to_dict, query_results_to_dict, get_match_history, get_match_history_by_games, get_match_history_by_players, get_match_history_by_players_and_games, get_wins_per_player
from app.services.bgg_import import import_games_from_bgg



# ---------------------
#   GAME MANAGEMENT
# ---------------------

games_bp = Blueprint('games', __name__)

@games_bp.route('/get_games', methods=['GET'])
@jwt_required()
def get_games():
    """Get all boardgames.

    Request: GET

    Returns: 
        JSON: 
            'games': list[dict<Model.Game>]
            or
            'error': str

    """

    try:
        games = find_all("games", {})
        games_data = query_results_to_dict(games)

        return jsonify(games_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@games_bp.route('/add_game', methods=['POST'])
@jwt_required()
def add_game():
    data = request.get_json()
    bgg_id = data.get('bgg_id')
    bgg_search = data.get('bgg_search')

    if bgg_search:
        # Get the game information from BGG API
        bgg_api_url = f"https://www.boardgamegeek.com/xmlapi2/thing?id={bgg_id}"
        response = requests.get(bgg_api_url)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch game information from BGG API'}), 500

        # Parse the XML response (assuming the response is in XML format)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        game = root.find('item')

        game_data = {
            'bgg_id': game.attrib['id'],
            'name': game.find('link[@type=\'primary\']').attrib['value'],
            'base_game_id': None if game.find('link[@type=\'boardgameexpansion\']') is None else game.find('link[@type=\'boardgameexpansion\']').attrib['id'],
            'min_players': game.find('minplayers').attrib['value'],
            'max_players': game.find('maxplayers').attrib['value'],
            'avg_duration': game.find('playingtime').attrib['value'],
            'year_published': game.find('yearpublished').attrib['value'] if game.find('yearpublished') is not None else None,
            'image': {'url': game.find('image').text,
                    'thumbnail': game.find('thumbnail').text
                    },
            'is_cooperative': False,
            'is_team_based': False, # if game.find('link[@id=\'2024\']') is None else True,
            'description': game.find('description').text,
            'belongs_to_user': None,
            'location': None,
            'rulebook': None,
            'scoring_sheet': None
        }
    
    else:
        game_data = {
            'bgg_id': bgg_id,
            'name': data.get('name'),
            'base_game_id': data.get('base_game_id'),
            'min_players': data.get('min_players'),
            'max_players': data.get('max_players'),
            'avg_duration': data.get('avg_duration'),
            'year_published': data.get('year_published'),
            'image': data.get('image_url'),
            'is_cooperative': data.get('is_cooperative', False),
            'is_team_based': data.get('is_team_based', False),
            'description': data.get('description'),
            'belongs_to_user': data.get('belongs_to_user'),
            'location': data.get('location'),
            'rulebook': data.get('rulebook'),
            'scoring_sheet': data.get('scoring_sheet')
        }

    if find_one("games", {'bgg_id': bgg_id, 'name': game_data['name']}) is None:
        insert_one("games", game_data)
        return jsonify({'message': 'Game added successfully'}), 201
    return jsonify({'error': 'Game already exists'}), 400

@games_bp.route('/import_games', methods=['GET'])
@jwt_required()
def import_games():
    # Import games from BGG API using the bgg_import.py

    # Get the username from the .env file
    username = os.getenv('BGG_USERNAME')

    # Check if the username is provided
    if not username:
        return jsonify({'error': 'Missing BGG username'}), 400
    
    import_games_from_bgg(username)
    return jsonify({'message': 'Games imported successfully'}), 200

@games_bp.route('/update_game', methods=['POST'])
@jwt_required()
def update_game():
    """Update existing boardgame.

    Request: POST
        game_id (int): The ID of the game to update.
        other game attributes (optionnal): See models

    Returns:
        JSON:
            'message' (str)
            or 'error' (str)

    """

    game_data = {
        'bgg_id': request.form.get('bgg_id'),
        'name': request.form.get('name'),
        'base_game_id': request.form.get('base_game_id'),
        'min_players': request.form.get('min_players'),
        'max_players': request.form.get('max_players'),
        'avg_duration': request.form.get('avg_duration'),
        'year_published': request.form.get('year_published'),
        'image': {'url': request.form.get('image_url'), 'thumbnail': request.form.get('image_thumbnail')},
        'is_cooperative': request.form.get('is_cooperative', False),
        'is_team_based': request.form.get('is_team_based', False),
        'description': request.form.get('description'),
        'belongs_to_user': request.form.get('belongs_to_user'),
        'location': request.form.get('location'),
        'rulebook': request.form.get('rulebook'),
        'scoring_sheet': request.form.get('scoring_sheet')
    }

    game_data_filtered = {k: v for k, v in game_data.items() if v is not None}


    game_id = request.form.get('game_id')

    if game_id:
        # Update the game in the database
        res = update_one("games", {'id': game_id}, game_data_filtered)
        if res:
            return jsonify({'message': 'Game updated successfully'}), 200
        else:
            return jsonify({'error': 'No modification applied'}), 400

    return jsonify({'error': 'Input not valid'}), 400

@games_bp.route('/remove_games', methods=['DELETE'])
@jwt_required()
def remove_games():
    """Remove existing boardgames.
    
        Request: POST
            game_id (int): The ID of the game to update.
    
        Returns:
            JSON:
                'message' (str)
                or 'error' (str)
    
        """
    return

@games_bp.route('/get_wishlists', methods=['GET'])
@jwt_required()
def get_wishlists(): # TODO
    """Get wishlist from players.

    Request: GET
        players: list[dict] (optionnal)
            List of players to get wishlist from else take all
            id: int
            username: str
            team: int (optionnal)

    Returns:
        JSON: 'games_id' as list[int] or 'error' as str

    """
    try:
        players = []
        index = 0
        while True:
            player_id = request.args.get(f"players[{index}][id]")
            # Check if another player is defined, else break loop
            if player_id is None:
                break
            players.append(player_id)
            index += 1
        
        wishlist_data = []
        if not players:
            wishlist = find_all("wishlists", {})
        else:
            for player_id in players:
                wishlist = find_all("wishlists", {'player_id': player_id})
                wishlist_data.extend(wishlist)
        
        wishlist_data = [elt.game_id for elt in wishlist]

        return jsonify({'games_id': wishlist_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@games_bp.route('/add_wishlist', methods=['POST'])
@jwt_required()
def add_wishlist():
    """Add games to player's wishlist.

    Request: POST
        players: list[dict] (optionnal)
            List of players to get wishlist from else take all
            id: int
            username: str
            team: int (optionnal)

    Returns: JSON
        JSON: 'games_id' as list[int] or 'error' as str

    """

    data = request.get_json()
    game_id = data.get('game_id')
    username = get_jwt_identity()

    if not game_id:
        return jsonify({'error': 'Missing game_id'}), 400

    user = find_one("players", {'username': username})
    if not user:
        return jsonify({'error': f"User {username} not found"}), 404

    wishlist_data = {
        'game_id': game_id,
        'player_id': user.id
    }

    # Check if the game is already in the wishlist
    wishlisted = find_one("wishlists", wishlist_data)

    if wishlisted:
        return jsonify({'error': f"Game already in the wishlist for {user.id}"}), 400
    else:
        game = find_one("games", {'id': game_id})

        if not game:
            return jsonify({'error': f"Failed to fetch game {game_id} information from Games DB"}), 500
        else:
            insert_one("wishlists", wishlist_data)

    return jsonify({'message': f"Game {game_id} added to {user.id}'s wishlist"}), 201

@games_bp.route('/remove_wishlist', methods=['DELETE'])
@jwt_required()
def remove_wishlist():
    """Remove elements from player's wishlist.

    Request: GET
        players: list[dict] (optionnal)
            List of players to get wishlist from else take all
            id (int), username (str), team (int, optionnal)

    Returns: JSON
        JSON: 
            'games_id': list[int]
            or
            'error': str

        """
    # Get the bgg id from the query string
    data = request.get_json()
    game_id = data.get('game_id')
    username = get_jwt_identity()

    if not game_id:
        return jsonify({'error': 'Missing game_id'}), 400

    user = find_one("players", {'username': username})
    if not user:
        return jsonify({'error': f"User {username} not found"}), 404
    
    # Check if the game is in the wishlist
    wishlisted = find_one("wishlists", {'game_id': game_id, 'player_id': user.id})
    if not wishlisted:
        return jsonify({'error': f"Game not found in {user.id}'s wishlist"}), 404
    
    # Remove the game from the wishlist
    delete_one("wishlists", {'game_id': game_id, 'player_id': user.id})

    return jsonify({'message': f"Game removed from {user.id}'s wishlist"}), 200
