from flask import Blueprint, jsonify, request

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from app.extensions.db import db
from app.models.survey import Survey
from app.decorators.roles import researcher_required

surveys_bp = Blueprint(
    "surveys",
    __name__,
    url_prefix="/surveys"
)

@surveys_bp.route("/", methods=["POST"])
@researcher_required()
def create_survey():

    data = request.get_json()

    survey = Survey(
        title=data.get("title"),
        description=data.get("description"),
        researcher_id=int(get_jwt_identity())
    )

    db.session.add(survey)
    db.session.commit()

    return jsonify({
        "message": "Survey created successfully",
        "survey_id": survey.id
    }), 201

@surveys_bp.route("/", methods=["GET"])
@jwt_required()
def get_surveys():

    surveys = Survey.query.all()

    result = []

    for survey in surveys:

        result.append({
            "id": survey.id,
            "title": survey.title,
            "description": survey.description,
            "researcher_id": survey.researcher_id
        })

    return jsonify(result), 200

@surveys_bp.route("/<int:survey_id>", methods=["GET"])
@jwt_required()
def get_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({
            "message": "Survey not found"
        }), 404

    return jsonify({
        "id": survey.id,
        "title": survey.title,
        "description": survey.description,
        "researcher_id": survey.researcher_id
    }), 200

@surveys_bp.route("/<int:survey_id>", methods=["PUT"])
@researcher_required()
def update_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({
            "message": "Survey not found"
        }), 404

    current_user_id = int(get_jwt_identity())

    if survey.researcher_id != current_user_id:
        return jsonify({
            "message": "Unauthorized"
        }), 403

    data = request.get_json()

    survey.title = data.get(
        "title",
        survey.title
    )

    survey.description = data.get(
        "description",
        survey.description
    )

    db.session.commit()

    return jsonify({
        "message": "Survey updated successfully"
    }), 200

@surveys_bp.route("/<int:survey_id>", methods=["DELETE"])
@researcher_required()
def delete_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({
            "message": "Survey not found"
        }), 404

    current_user_id = int(get_jwt_identity())

    if survey.researcher_id != current_user_id:
        return jsonify({
            "message": "Unauthorized"
        }), 403

    db.session.delete(survey)
    db.session.commit()

    return jsonify({
        "message": "Survey deleted successfully"
    }), 200



