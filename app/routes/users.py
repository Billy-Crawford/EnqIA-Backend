from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from app.decorators.roles import admin_required
from app.extensions.db import db
from app.models.user import User

users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users"
)


@users_bp.route("/", methods=["GET"])
@admin_required()
def get_users():

    users = User.query.all()

    result = []

    for user in users:
        result.append({
            "id": user.id,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "role": user.role
        })

    return jsonify(result), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
@admin_required()
def get_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    return jsonify({
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "role": user.role
    }), 200


@users_bp.route("/", methods=["POST"])
@admin_required()
def create_user():

    data = request.get_json()

    existing_user = User.query.filter_by(
        email=data.get("email")
    ).first()

    if existing_user:
        return jsonify({
            "message": "Email already exists"
        }), 400

    user = User(
        firstname=data.get("firstname"),
        lastname=data.get("lastname"),
        email=data.get("email"),
        password=generate_password_hash(
            data.get("password")
        ),
        role=data.get("role")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully"
    }), 201

@users_bp.route("/<int:user_id>", methods=["PUT"])
@admin_required()
def update_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    data = request.get_json()

    user.firstname = data.get(
        "firstname",
        user.firstname
    )

    user.lastname = data.get(
        "lastname",
        user.lastname
    )

    user.email = data.get(
        "email",
        user.email
    )

    user.role = data.get(
        "role",
        user.role
    )

    db.session.commit()

    return jsonify({
        "message": "User updated successfully"
    }), 200

@users_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required()
def delete_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully"
    }), 200


