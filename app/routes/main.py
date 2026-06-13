from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    return jsonify({
        "project": "EnqIA",
        "message": "API is running successfully | C'EST TOUJOURS BIEN FAIT"
    })

