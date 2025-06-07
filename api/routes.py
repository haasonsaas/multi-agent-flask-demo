"""
API routes for the Flask dashboard
"""
from flask import Blueprint, jsonify, request
from database import get_db_instance
from models import ScrapingResult
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

# Get database instance
db = get_db_instance()


@api_bp.route('/results', methods=['GET'])
def get_all_results():
    """Get all scraping results with optional pagination."""
    try:
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        results = db.get_all_scraping_results(limit=limit, offset=offset)
        return jsonify({
            'results': [r.to_dict() for r in results],
            'count': len(results),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        logger.error(f"Error fetching results: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/results/<int:result_id>', methods=['GET'])
def get_result(result_id):
    """Get a specific scraping result by ID."""
    try:
        result = db.get_scraping_result(result_id)
        if not result:
            return jsonify({'error': 'Result not found'}), 404
        return jsonify(result.to_dict())
    except Exception as e:
        logger.error(f"Error fetching result {result_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get aggregated statistics."""
    try:
        stats = db.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/results', methods=['POST'])
def create_result():
    """Add a new scraping result."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['url', 'agent_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        result = db.create_scraping_result(data)
        return jsonify(result.to_dict()), 201
    except Exception as e:
        logger.error(f"Error creating result: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500