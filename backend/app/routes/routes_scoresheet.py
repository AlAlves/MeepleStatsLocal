from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required

import os
import json

scoresheets_bp = Blueprint('scoresheets', __name__)

@scoresheets_bp.route('/get_scoresheets', methods=['GET'])
@jwt_required()
def get_scoresheets():
    try:

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        SCORESHEETS_DIR = os.path.join(BASE_DIR, "scoresheets")

        if not os.path.exists(SCORESHEETS_DIR):
            os.makedirs(SCORESHEETS_DIR)

        # Get all scoresheets from the folder
        scoresheets = [f for f in os.listdir(SCORESHEETS_DIR) if f.endswith('.json')]
        # Get only the game name --> remove the _score_sheet.json
        scoresheets = [f.replace('_score_sheet.json', '') for f in scoresheets]
        return jsonify(scoresheets), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scoresheets_bp.route('/scoresheets/<sheet_name>', methods=['GET'])
@jwt_required()
def get_scoresheet(sheet_name):
    try:

        filename = f"{sheet_name}_score_sheet.json"
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        SCORESHEETS_DIR = os.path.join(BASE_DIR, "scoresheets")
        file_path = os.path.join(SCORESHEETS_DIR, filename)


        if not os.path.exists(file_path):
            return jsonify({'error': 'Score sheet not found'}), 404
        
        return send_from_directory(SCORESHEETS_DIR, filename, mimetype='application/json')

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@scoresheets_bp.route('/upload_scoresheet', methods=['POST'])
@jwt_required()
def upload_scoresheet():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No scoresheet provided'}), 400

        game_name = data.get('game_name')
        if not game_name:
            return jsonify({'error': 'No game name provided'}), 400
        
        file_name = f"{game_name}_score_sheet.json"
        
        # Save file locally as fallback
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        SCORESHEETS_DIR = os.path.join(BASE_DIR, "scoresheets")

        if not os.path.exists(SCORESHEETS_DIR):
            os.makedirs(SCORESHEETS_DIR)

        file_path = os.path.join(SCORESHEETS_DIR, file_name)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        return jsonify({'message': 'Score sheet uploaded successfully', 'file_url': f"/scoresheets/{file_name}"}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
