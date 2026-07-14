from flask import Blueprint, jsonify
from analytics import get_dashboard_stats

ml_bp = Blueprint('ml', __name__, url_prefix='/api')

@ml_bp.route('/stats')
def stats():
    # Returns JSON data for Chart.js in the admin dashboard
    data = get_dashboard_stats()
    return jsonify(data)
