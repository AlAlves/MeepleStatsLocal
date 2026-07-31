from datetime import datetime

from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity

import os
import uuid
from flask import current_app

from app.services.db import find_one, find_all, insert_one, update_one, delete_one, query_result_to_dict, query_results_to_dict, get_match_history, get_match_history_by_games, get_match_history_by_players, get_match_history_by_players_and_games, get_wins_per_player
from app.services.bgg_import import import_games_from_bgg

from app.services.rag import query_llm, query_index, display_search_results, initialize_pinecone, create_safe_namespace, index_single_pdf, clear_namespace


# if os.getenv('ENABLE_RAG') == 'True':
#     index, embedding_provider = initialize_pinecone()

STORAGE_TYPE = os.getenv('STORAGE_TYPE') #'local'

upload_folder = None

if STORAGE_TYPE in ['local']:
    # Create the upload folder if it doesn't exist
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)


rulebooks_bp = Blueprint('rulebooks', __name__)

@rulebooks_bp.route('/get_rulebooks', methods=['GET'])
@jwt_required()
def get_rulebooks():
    try:
        # Get all rulebooks from database
        rulebooks = find_all("rulebooks", {})
        
        rulebooks_data = []
        for rulebook in rulebooks:
            rulebook['_id'] = str(rulebook['_id'])
            rulebooks_data.append(rulebook)
            
        return jsonify(rulebooks_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rulebooks_bp.route('/rulebook/<rulebook_id>', methods=['GET'])
@jwt_required()
def get_rulebook(rulebook_id):
    try:
        # Find rulebook
        rulebook = find_one("rulebooks", {'_id': rulebook_id})
        
        if not rulebook:
            return jsonify({'error': 'Rulebook not found'}), 404
            
        # Convert ObjectId to string
        rulebook['_id'] = str(rulebook['_id'])
        
        return jsonify(rulebook), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rulebooks_bp.route('/upload_rulebook', methods=['POST'])
@jwt_required()
def upload_rulebook():
    try:
        # Get current user
        current_user = get_jwt_identity()
        
        # Check if PDF file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Check if file is PDF
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'File must be PDF'}), 400
            
        # Get game information
        game_id = request.form.get('game_id')
        game_name = request.form.get('game_name')
        
        # Create unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        
        # Always use S3 for rulebooks
        if STORAGE_TYPE == 's3':
            # Save file to S3
            S3Client.put(file, unique_filename, content_type='application/pdf')
            file_url = S3Client.get_url_from_filename(unique_filename)
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file_path = temp_file.name
                
            # Download from S3 to temp file
            S3Client.download(unique_filename, temp_file_path)
            
            index_single_pdf(file.filename, index, embedding_provider, temp_file_path)

            # Clean up
            os.remove(temp_file_path)
        else:
            # Save file locally as fallback
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            file_url = f"/uploads/{unique_filename}"
            index_single_pdf(file.filename, index, embedding_provider, file_path)
            
        # Save rulebook info to database
        rulebook_data = {
            'filename': file.filename,
            'file_url': file_url,
            'game_id': game_id,
            'game_name': game_name,
            'uploaded_by': current_user,
            'uploaded_at': datetime.now(),
            'original_uploader': current_user
        }
        
        insert_one("rulebooks", rulebook_data)
        
        return jsonify({'message': 'Rulebook uploaded successfully', 'file_url': file_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rulebooks_bp.route('/rulebook/<rulebook_id>', methods=['DELETE'])
@jwt_required()
def delete_rulebook(rulebook_id):
    try:
        # Get current user
        current_user = get_jwt_identity()
        
        # Find rulebook
        rulebook = find_one("rulebooks", {'_id': rulebook_id})
        
        if not rulebook:
            return jsonify({'error': 'Rulebook not found'}), 404
            
        # Check if user is the one who uploaded the rulebook
        if rulebook['uploaded_by'] != current_user:
            return jsonify({'error': 'Unauthorized to delete this rulebook'}), 403
            
        # Delete from database
        delete_one("rulebooks", {'_id': rulebook_id})
        
        clear_namespace(index, create_safe_namespace(rulebook['filename']))

        # Delete the actual file based on storage type
        if STORAGE_TYPE == 'local':
            filename = os.path.basename(rulebook['file_url'])
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        elif STORAGE_TYPE == 's3':
            file_url = rulebook['file_url']
            if file_url:
                filename = file_url.split('/')[-1]
                S3Client.delete(filename)
                
        return jsonify({'message': 'Rulebook deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rulebooks_bp.route('/ask_rulebook', methods=['POST'])
@jwt_required()
def ask_rulebook():
    try:
        # Get current user
        current_user = get_jwt_identity()
        
        # Get query and rulebook ID from request
        data = request.json
        query = data.get('query')
        rulebook_id = data.get('rulebook_id')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        if not rulebook_id:
            return jsonify({'error': 'No rulebook ID provided'}), 400
        
        # Find rulebook
        rulebook = find_one("rulebooks", {'_id': rulebook_id})
        
        if not rulebook:
            return jsonify({'error': 'Rulebook not found'}), 404
        
        # Import the RAG functionality
        
        
        # Get the safe namespace for the rulebook (filename without extension)
        filename = rulebook.get('filename', '')
        namespace = create_safe_namespace(filename)
        
        # Initialize embedding model and Pinecone
        #embedding_model = initialize_embedding_model()
        #index = initialize_pinecone()
        
        # Query Pinecone
        top_matches = query_index(query, [namespace], index, embedding_provider)
        
        # No matches found
        if not top_matches:
            response_payload = {
                'answer': "I couldn't find any relevant information in this rulebook to answer your question. Please try rephrasing your query or check if this rulebook contains information about this topic.",
                'page_refs': []
            }
            
            # Include context only if requested
            include_context = data.get('include_context', False)
            if include_context:
                response_payload['context'] = ""
                
            return jsonify(response_payload), 200
        
        # Process the results
        context, page_refs = display_search_results(top_matches)
        
        # Ensure page_refs are properly serializable
        serializable_page_refs = []
        for ref in page_refs:
            serializable_page_refs.append({
                "page": str(ref["page"]),
                "file": str(ref["file"])
            })
        
        # Ensure context is a string
        if not isinstance(context, str):
            context = str(context)
        
        # Query the LLM
        answer = query_llm(query, context, page_refs)
        
        # Ensure answer is a string
        if not isinstance(answer, str):
            answer = str(answer)
        
        # Create a response payload with only JSON-serializable types
        response_payload = {
            'answer': answer,
            # Only include context if explicitly requested with include_context=true
            'page_refs': serializable_page_refs
        }
        
        # Include context only if requested
        include_context = data.get('include_context', False)
        if include_context:
            response_payload['context'] = context
        
        # Convert to JSON string and back to dict to ensure all objects are serializable
        try:
            import json
            response_json = json.dumps(response_payload)
            response_payload = json.loads(response_json)
        except TypeError as e:
            print(f"JSON serialization error: {str(e)}")
            # Fallback response if serialization fails
            response_payload = {
                'answer': "I processed your query but encountered an error formatting the response. Please try again.",
                'page_refs': []
            }
            if include_context:
                response_payload['context'] = ""
        
        return jsonify(response_payload), 200
        
    except Exception as e:
        error_message = str(e)
        print(f"Error in rulebook chat: {error_message}")
        
        # Add more detailed debugging
        import traceback
        traceback.print_exc()
        
        # Try to identify the problematic object type
        if "is not JSON serializable" in error_message:
            try:
                import inspect
                print(f"Attempting to identify non-serializable object...")
                if "page_refs" in locals():
                    print(f"page_refs type: {type(page_refs)}")
                    if page_refs and len(page_refs) > 0:
                        print(f"First page_ref item type: {type(page_refs[0])}")
                if "context" in locals():
                    print(f"context type: {type(context)}")
                if "answer" in locals():
                    print(f"answer type: {type(answer)}")
            except Exception as debug_error:
                print(f"Error during debugging: {str(debug_error)}")
        
        return jsonify({
            'error': error_message, 
            'message': 'An error occurred while processing your request'
        }), 500
