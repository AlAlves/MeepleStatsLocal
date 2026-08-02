from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity


from app.services.db import find_one, find_all, insert_one, update_one, delete_one, query_result_to_dict, query_results_to_dict, get_match_history, get_match_history_by_games, get_match_history_by_players, get_match_history_by_players_and_games, get_wins_per_player
from app.services.bgg_import import import_games_from_bgg


statistic_bp = Blueprint('statistic', __name__)

### GLOBAL STATS ###

@statistic_bp.route('/get_total_hours', methods=['GET'])
@jwt_required()
def get_total_hours():
    """Compute total nb of hours spend in game TODO

    Returns:
        _type_: _description_
    """

    # Get date filters from query string
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Check if the date filters are provided and validate them
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    else:
        start_date = datetime(1970, 1, 1) # Default start date
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    else:
        end_date = datetime.now()
    
    date_query = {
        'date': {"$gte": start_date, "$lte": end_date}
        }

    # Get players
    index = 0
    players = []
    while True:
        player_id = request.form.get(f"players[{index}][id]") or None
        # Check if another player is defined, else break loop
        if player_id is None:
            break
        players.append(player_id)
        index += 1

    # Get games
    index = 0
    games = []
    while True:
        game_id = request.form.get(f"games[{index}][id]") or None
        # Check if another game is defined, else break loop
        if game_id is None:
            break
        games.append(game_id)
        index += 1

    try:
        if players:
            if games:
                results = get_match_history_by_players_and_games(players, games, date_query)
            else:
                results = get_match_history_by_players(players, date_query)
        else:
            if games:
                results = get_match_history_by_games(games, date_query)
            else:
                results = get_match_history(date_query)
        
        if results:
            total_duration = sum(match.duration for match in results if match.duration is not None)
            total_hours = round(total_duration / 60, 2)
        else:
            total_hours = 0

        return jsonify({
            "type": 'number',
            "value": total_hours,
            "unit": "hours",
            "description": "Total hours played between " + start_date.strftime('%Y-%m-%d') + " and " + end_date.strftime('%Y-%m-%d')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@statistic_bp.route('/get_total_matches', methods=['GET'])
@jwt_required()
def get_total_matches():
    """Get total nb of matches TODO

    Returns:
        _type_: _description_
    """

    # Get date filters from query string
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Check if the date filters are provided and validate them
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    else:
        start_date = datetime(1970, 1, 1) # Default start date

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    else:
        end_date = datetime.now()
    
    date_query = {
        "date": {"$gte": start_date, "$lte": end_date}
        }

    # Get players
    index = 0
    players = []
    while True:
        player_id = request.form.get(f"players[{index}][id]") or None
        # Check if another player is defined, else break loop
        if player_id is None:
            break
        players.append(player_id)
        index += 1

    # Get games
    index = 0
    games = []
    while True:
        game_id = request.form.get(f"games[{index}][id]") or None
        # Check if another game is defined, else break loop
        if game_id is None:
            break
        games.append(game_id)
        index += 1
    
    try:
        if players:
            if games:
                results = get_match_history_by_players_and_games(players, games, date_query)
            else:
                results = get_match_history_by_players(players, date_query)
        else:
            if games:
                results = get_match_history_by_games(games, date_query)
            else:
                results = get_match_history(date_query)
        
        # Find matches in the date range
        total_matches = len(results) if results else 0

        return jsonify({
            "type": "number",
            "value": total_matches,
            "unit": "matches",
            "description": "Total matches played between " + start_date.strftime('%Y-%m-%d') + " and " + end_date.strftime('%Y-%m-%d')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
### PLAYER STATS ###
@statistic_bp.route('/get_players_wins', methods=['GET'])
@jwt_required()
def get_players_wins():
    """Get win matches from set of players

    Returns:
        _type_: _description_
    """

    # Get date filters from query string
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Get player name from query string
    player_name = request.args.get('username')

    # Get players
    index = 0
    players = []
    while True:
        player_id = request.form.get(f"players[{index}][id]") or None
        # Check if another player is defined, else break loop
        if player_id is None:
            break
        players.append(player_id)
        index += 1

    # Check if the player name is provided otherwise use the logged user
    if not players:
        username = get_jwt_identity()
        player = find_one("players", {'username': username})
        players.append(player.id)

    # Check if the date filters are provided and validate them
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
    
    date_query = {
        "date": {"$gte": start_date, "$lte": end_date}
        }

    if start_date_str is None and end_date_str is None:
        results = get_wins_per_player(players, date_query)

        # Read from player's collection
        return jsonify({
            "type": "number",
            "value": player['wins'],
            "unit": "wins",
            "description": "Total wins of player " + player_name
        }), 200
    else:

        # Set default values for start_date and end_date if not provided
        if start_date_str is None:
            start_date = datetime(1970, 1, 1)
        if end_date_str is None:
            end_date = datetime.now()
        
        date_query = {
            "date": {"$gte": start_date, "$lte": end_date}
            }

        # Find matches in the date range from the player's collection where the player is the winner
        pipeline = [
            {
                "$match": {
                    "username": player_name
                }
            },
            {
                "$project": {
                    "matches": {
                        "$filter": {
                            "input": "$matches",
                            "as": "match",
                            "cond": {
                                "$let": {
                                    "vars": {
                                        # Convert the string date to a date object
                                        "match_date_obj": {
                                            "$dateFromString": {
                                                "dateString": "$$match.date", # Use the correct field name ('date')
                                                "format": "%Y-%m-%d",
                                                "onError": None, # Return null if conversion fails
                                                "onNull": None   # Return null if date string is null
                                            }
                                        }
                                    },
                                    "in": {
                                        "$and": [
                                            {"$ne": ["$$match_date_obj", None]}, # Ensure conversion was successful
                                            {"$eq": ["$$match.is_winner", True]},
                                            {"$gte": ["$$match_date_obj", start_date]}, # Compare date objects
                                            {"$lte": ["$$match_date_obj", end_date]}   # Compare date objects
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            },
            {
                "$unwind": "$matches"
            },
            {
                "$count": "total_wins"
            }
        ]

        # TODO: Use the find_all function to execute the aggregation pipeline instead of directly using the collection
        result = list(players_collection.aggregate(pipeline))

        if result:
            total_wins = result[0]["total_wins"]
        else:
            total_wins = 0

        return jsonify({
            "type": "number",
            "value": total_wins,
            "unit": "wins",
            "description": "Total wins of player " + player_name + " between " + start_date.strftime('%Y-%m-%d') + " and " + end_date.strftime('%Y-%m-%d')
        }), 200
                

@statistic_bp.route('/get_players_winrate', methods=['GET'])
@jwt_required()
def get_players_winrate():
    """Compute winrate from a set of players TODO

    Returns:
        _type_: _description_
    """

    # Get date filters from query string
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Get player name from query string
    player_name = request.args.get('username')

    # Check if the player name is provided otherwise use the logged user
    if not player_name:
        player_name = get_jwt_identity()
    
    # Check if the date filters are provided and validate them
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400

    player = find_one("players", {'username': player_name})

    if start_date_str is None and end_date_str is None:
        # Read from player's collection, prevent division by zero
        if player['total_matches'] > 0:
            winrate = (player['wins'] / player['total_matches']) * 100
        else:
            winrate = 0
        
        return jsonify({
            "type": "percentage",
            "value": winrate,
            "unit": "%",
            "description": "Winrate of player " + player_name
        }), 200
    else:
        
        # Set default values for start_date and end_date if not provided
        if start_date_str is None:
            start_date = datetime(1970, 1, 1)
        if end_date_str is None:
            end_date = datetime.now()

        # Calculate the win rate over a period of time from the player's collection

        # Find matches in the date range from the player's collection

        pipeline = [
            # 1. Filter the player by username
            {
                "$match": {
                    "username": player_name
                }
            },
            # 2. Filter matches by date range
            {
                "$project": {
                    "matches": {
                        "$filter": {
                            "input": "$matches",
                            "as": "match",
                            "cond": {
                                "$let": {  # Use $let to define a temporary variable
                                    "vars": {
                                        "match_date_obj": {
                                            "$dateFromString": {
                                                "dateString": "$$match.date", # Convert the date string
                                                "format": "%Y-%m-%d",
                                                "onError": None,
                                                "onNull": None
                                            }
                                        }
                                    },
                                    "in": {
                                        "$and": [
                                            {"$ne": ["$$match_date_obj", None]}, # Ensure conversion was successful
                                            {"$gte": ["$$match_date_obj", start_date]}, # Compare date objects
                                            {"$lte": ["$$match_date_obj", end_date]}   # Compare date objects
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            },
            # 3. Unwind the matches array
            {
                "$unwind": "$matches"
            },
            # 4. Group by the player (or any field, since we're calculating a total)
            {
                "$group": {
                    "_id": None,  # We don't need a specific group key
                    "total_matches": {"$sum": 1},
                    "total_wins": {"$sum": {"$cond": [{"$eq": ["$matches.is_winner", True]}, 1, 0]}}
                }
            },
            # 5. Calculate the winrate
            {
                "$project": {
                    "total_matches": 1,
                    "total_wins": 1,
                    "winrate": {
                        "$cond": [
                            {"$gt": ["$total_matches", 0]},
                            {"$multiply": [{"$divide": ["$total_wins", "$total_matches"]}, 100]},
                            0  # If no matches, winrate is 0
                        ]
                    }
                }
            }
        ]

        # TODO: Use the find_all function to execute the aggregation pipeline instead of directly using the collection
        result = list(players_collection.aggregate(pipeline))

        if result:
            winrate = result[0]["winrate"]
            return jsonify({
                "type": "percentage",
                "value": winrate,
                "unit": "%",
                "description": "Winrate of player " + player_name + " between " + start_date.strftime('%Y-%m-%d') + " and " + end_date.strftime('%Y-%m-%d')
            }), 200
        else:
            return jsonify({
                "type": "percentage",
                "value": 0,
                "unit": "%",
                "description": "Winrate of player " + player_name + " between " + start_date.strftime('%Y-%m-%d') + " and " + end_date.strftime('%Y-%m-%d')
            }), 200

@statistic_bp.route('/get_players_longest_winstreak', methods=['GET'])
@jwt_required()
def get_players_longest_winstreak():
    """Get longest winstreak from a set of players TODO

    Returns:
        _type_: _description_
    """

    # Get player name from query string
    player_name = request.args.get('username')

    # Check if the player name is provided otherwise use the logged user
    if not player_name:
        player_name = get_jwt_identity()

    player = find_one("players", {'username': player_name})

    return jsonify({
        "type": "number",
        "value": player['longest_winstreak'],
        "unit": "matches",
        "description": "Longest win streak of player " + player_name
    }), 200

@statistic_bp.route('/get_players_games_wins', methods=['GET'])
@jwt_required()
def get_players_games_wins():
    """TODO: Get nb of win per game for a set of players.

    Returns:
        JSON: user, game, nb_win
    """

    # Get player name from query string
    player_name = request.args.get('username')

    # Check if the player name is provided otherwise use the logged user
    if not player_name:
        player_name = get_jwt_identity()
    
    # Calculate the game with most wins and with least wins from player collection

    pipeline = [
        # 1. Filter the player by username
        {
            "$match": {
                "username": player_name
            }
        },
        # 2. Unwind the matches array
        {
            "$unwind": "$matches"
        },
        # 3. Group by game_id
        {
            "$group": {
                "_id": "$matches.game_id",
                "total_wins": {"$sum": {"$cond": [{"$eq": ["$matches.is_winner", True]}, 1, 0]}}
            }
        },
        # 4. Sort by total_wins in descending order
        {
            "$sort": {
                "total_wins": -1
            }
        }
    ]

    # TODO: Use the find_all function to execute the aggregation pipeline instead of directly using the collection
    result = list(players_collection.aggregate(pipeline))

    if result:
        # Get the games' names from the game collection
        best_game = find_one("games", {"bgg_id": result[0]["_id"]})
        worst_game = find_one("games", {"bgg_id": result[-1]["_id"]})
        
        best_game_name = best_game["name"] if best_game else "Unknown"
        worst_game_name = worst_game["name"] if worst_game else "Unknown"
        return jsonify({
            "type": "comparison",
            "value": [
                {
                    "name": best_game_name,
                    "game_id": result[0]["_id"],
                    "total_wins": result[0]["total_wins"],
                    "status": "best"
                },
                {
                    "name": worst_game_name,
                    "game_id": result[-1]["_id"],
                    "total_wins": result[-1]["total_wins"],
                    "status": "worst"
                }
            ],
            "unit": "wins",
            "description": "Best and worst game played by player " + player_name
        }), 200
    else: 
        return jsonify({
            "type": "comparison",
            "value": [],
            "unit": "wins",
            "description": "No matches found for player " + player_name,
        }), 404
    
### GAME STATS ###

@statistic_bp.route('/get_game_coop_winrate', methods=['GET'])
@jwt_required()
def get_game_coop_winrate():
    """Get winrate from coop games TODO

    Returns:
        _type_: _description_
    """

    # This route return the winrate of cooperative games for all the coop games in the collection if no game_id is provided
    
    # Calculate the win rate of cooperative matches for a specific game from game collection

    game_name = request.args.get('game_name')

    if not game_name:
        pipeline = [
            # 1. Filter the games by is_cooperative
            {
                "$match": {
                    "is_cooperative": True
                }
            },
            # 2. Unwind the matches array
            {
                "$unwind": "$matches"
            },
            # 3. Group by game_id
            {
                "$group": {
                    "_id": "$bgg_id",
                    "total_matches": {"$sum": 1},
                    "total_wins": {"$sum": {"$cond": [ {"$gt": [{"$size": "$matches.winner"}, 0]},
                            1,
                            0]}}
                }
            },
            # 4. Calculate the winrate
            {
                "$project": {
                    "game_id": "$_id",
                    "total_matches": 1,
                    "total_wins": 1,
                    "winrate": {
                        "$cond": [
                            {"$gt": ["$total_matches", 0]},
                            {"$multiply": [{"$divide": ["$total_wins", "$total_matches"]}, 100]},
                            0
                        ]
                    }
                }
            },
            # 5. Sort by winrate in descending order
            {
                "$sort": {
                    "winrate": -1
                }
            },
            # 6. Limit to the top 5
            {
                "$limit": 5
            }
        ]
    else: 
        pipeline = [
            # 1. Filter the games by game_name
            {
                "$match": {
                    "name": game_name,
                    "is_cooperative": True
                }
            },
            # 2. Unwind the matches array
            {
                "$unwind": "$matches"
            },
            # 3. Group by game_id
            {
                "$group": {
                    "_id": "$bgg_id",
                    "total_matches": {"$sum": 1},
                    "total_wins": {"$sum": {"$cond": [ {"$gt": [{"$size": "$matches.winner"}, 0]},
                            1,
                            0]}}
                }
            },
            # 4. Calculate the winrate
            {
                "$project": {
                    "game_id": "$_id",
                    "total_matches": 1,
                    "total_wins": 1,
                    "winrate": {
                        "$cond": [
                            {"$gt": ["$total_matches", 0]},
                            {"$multiply": [{"$divide": ["$total_wins", "$total_matches"]}, 100]},
                            0
                        ]
                    }
                }
            }
        ]
    # TODO: Use the find_all function to execute the aggregation pipeline instead of directly using the collection
    result = list(games_collection.aggregate(pipeline))

    if result:
        for game in result:
            game_data = find_one("games", {"bgg_id": game["game_id"]})
            game["name"] = game_data["name"] if game_data else "Unknown"
            # Remove the game_id from the result
            del game["game_id"]
        
        return jsonify({
            "type": "list",
            "value": result,
            "description": "Top 5 cooperative games winrate"
        }), 200
    else:
        return jsonify({
            "type": "list",
            "value": [],
            "description": "No cooperative games found"
        }), 200

@statistic_bp.route('/get_game_nb_matches', methods=['GET'])
@jwt_required()
def get_game_nb_matches():
    """Get nb of matches for a given game TODO

    Returns:
        _type_: _description_
    """
        
    # Calculate the number of matches for a specific game from game collection

    pipeline = [
        # 1. Unwind the matches array
        {
            "$unwind": "$matches"
        },
        # 2. Group by game_id
        {
            "$group": {
                "_id": "$bgg_id",
                "total_matches": {"$sum": 1}
            }
        },
        # 3. Sort by total_matches in descending order
        {
            "$sort": {
                "total_matches": -1
            }
        }
    ]

    result = list(games_collection.aggregate(pipeline))

    if result:

        # Get the games' names from the game collection
        # TODO check most played and not bgg id ?
        most_played = find_one("games", {"bgg_id": result[0]["_id"]})
        least_played = find_one("games", {"bgg_id": result[-1]["_id"]})
        
        most_played_name = most_played["name"] if most_played else "Unknown"
        least_played_name = least_played["name"] if least_played else "Unknown"
    

        return jsonify({
            "type": "comparison",
            "value": [
                {
                    "name": most_played_name,
                    "game_id": result[0]["_id"],
                    "total_matches": result[0]["total_matches"],
                    "status": "most"
                },
                {
                    "name": least_played_name,
                    "game_id": result[-1]["_id"],
                    "total_matches": result[-1]["total_matches"],
                    "status": "least"
                }
            ],
            "description": "Most and least played games",
        }), 200
    else:
        return jsonify({
            "type": "comparison",
            "value": [],
            "description": "No matches found",
        }), 200
        
@statistic_bp.route('/get_games_avg_duration', methods=['GET'])
@jwt_required()
def get_games_avg_duration():
    """Get average duration from a set of games TODO

    Returns:
        _type_: _description_
    """

    # Get game from query string
    game_name = request.args.get('game_name')

    if not game_name:
        # Retourn the top 3 games with the highest average duration
        pipeline = [
            # 1. Unwind the matches array
            {
                "$unwind": "$matches"
            },
            # 2. Group by game_id
            {
                "$group": {
                    "_id": "$bgg_id",
                    "average_duration": {"$avg": {"$toInt": "$matches.game_duration"}}
                }
            },
            # 3. Sort by average_duration in descending order
            {
                "$sort": {
                    "average_duration": -1
                }
            },
            # 4. Limit to the top 3
            {
                "$limit": 3
            }
        ]
    else:
        pipeline = [
            # 1. Filter the games by game_name
            {
                "$match": {
                    "name": game_name
                }
            },
            # 2. Unwind the matches array
            {
                "$unwind": "$matches"
            },
            # 3. Group by game_id
            {
                "$group": {
                    "_id": "$bgg_id",
                    "average_duration": {"$avg": "$matches.game_duration"}
                }
            }
        ]

    # TODO: Use the find_all function to execute the aggregation pipeline instead of directly using the collection
    result = list(games_collection.aggregate(pipeline))

    if result:
        # Add game names to results
        for game in result:
            game_data = find_one("games", {"bgg_id": game["_id"]})
            game["name"] = game_data["name"] if game_data else "Unknown"

        if game_name:
            return jsonify({
                "type": "number",
                "value": result[0]["average_duration"],
                "unit": "hours",
                "description": f"Average duration for {game_name}"
            }), 200
        else:
            return jsonify({
                "type": "list",
                "value": result,
                "description": "Games with longest average duration"
            }), 200
    else:
        return jsonify({
            "type": "number",
            "value": 0,
            "unit": "hours",
            "description": f"No data available for {game_name if game_name else 'any game'}"
        }), 200


@statistic_bp.route('/get_game_best_value', methods=['GET'])
@jwt_required()
def get_game_best_value():
    """Get top `x` games with the best price/tot_hours_played ratio TODO

    Returns:
        JSON: _description_
    """

    # Get top 3 games with the best price/tot_hours_played ratio

    pipeline = [
        {
            '$match': { # Filter out documents where price is null or doesn't exist
                'price': {'$ne': None, '$exists': True},
                'isGifted': {'$ne': True} # Exclude gifted games
            }
        },
        {
            '$unwind': '$matches'
        },
        {
            '$group': {
                '_id': '$bgg_id',
                'name': {'$first': '$name'},
                'price': {'$first': '$price'},
                'total_minutes_played': {'$sum': {"$toInt":'$matches.game_duration'}}
            }
        },
        {
            '$addFields': {
                 # Calculate total hours played
                'total_hours_played': {'$divide': ['$total_minutes_played', 60]}
            }
        },
        {
            '$project': {
                'name': 1,
                'price': 1,
                'price_per_hour': {'$cond': [
                    {'$gt': ['$total_hours_played', 0]}, 
                    {'$round': [{'$divide': ['$price', '$total_hours_played']}, 2]},
                    None
                ]}
            }
        },
        {
           '$match': { # Filter out results where price_per_hour couldn't be calculated (e.g., 0 hours)
               'price_per_hour': {'$ne': None}
           }
        },
        {
            '$sort': {'price_per_hour': 1}
        },
        {
            '$limit': 3
        }
    ]

    # TODO: Use the find_all function to execute the aggregation pipeline instead of directly using the collection
    result = list(games_collection.aggregate(pipeline))

    if result:
        return jsonify({
            "type": "list",
            "value": result,
            "description": "Top 3 games with the best price/tot_hours_played ratio"
        }), 200
    else:
        return jsonify({
            "type": "list",
            "value": [],
            "description": "No games found"
        }), 200
    
@statistic_bp.route('/get_games_highest_score', methods=['GET'])
@jwt_required()
def get_games_highest_score():
    """Get highest score from a set of games TODO

    Returns:
        _type_: _description_
    """

    # Get the game name from query string
    game_name = request.args.get('game_name')

    # Check if the game name is provided
    if not game_name:
        return jsonify({
            "type": "number",
            "value": 0,
            "unit": "points",
            "description": "Missing game name"
        }), 200
    
    game = find_one("games", {'name': game_name})

    if not game:
        return jsonify({
            "type": "number",
            "value": 0,
            "unit": "points",
            "description": f"Game {game_name} not found"
        }), 200

    return jsonify({
        "type": "number",
        "value": game['record_score_by_player']['score'],
        "unit": "points",
        "description": f"Highest score for {game_name} is {game['record_score_by_player']['score']} points by {game['record_score_by_player']['name']}",
        "details": {
            "player": game['record_score_by_player']['name'],
            "player_id": game['record_score_by_player']['id']
        }
    }), 200

@statistic_bp.route('/get_games_avg_score', methods=['GET'])
@jwt_required()
def get_games_avg_score():
    """Get average score from a set of games TODO

    Returns:
        _type_: _description_
    """

    # Get the game name from query string
    game_name = request.args.get('game_name')

    # Check if the game name is provided
    if not game_name:
        return jsonify({
            "type": "number",
            "value": 0,
            "unit": "points",
            "description": "Missing game name"
        }), 200
    
    game = find_one("games", {'name': game_name})

    if not game:
        return jsonify({
            "type": "number",
            "value": 0,
            "unit": "points",
            "description": f"Game {game_name} not found"
        }), 200

    return jsonify({
        "type": "number",
        "value": round(game['average_score'], 2),
        "unit": "points",
        "description": f"Average score for {game_name} is {round(game['average_score'], 2)} points"
    }), 200
