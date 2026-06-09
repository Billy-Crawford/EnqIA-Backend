from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    return jsonify({
        "project": "EnsIA",
        "message": "API is running successfully"
    })

