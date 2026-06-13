from datetime import datetime

from flasgger import swag_from
from flask import Blueprint, jsonify, request

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity, get_jwt
)

from app.extensions.db import db
from app.models.answer import Answer
from app.models.survey import Survey
from app.decorators.roles import researcher_required

from flask import send_file
from io import BytesIO

from app.services.event_logger import log_event
from app.services.export_service import (
    generate_csv_export,
    generate_excel_export
)

surveys_bp = Blueprint(
    "surveys",
    __name__,
    url_prefix="/surveys"
)

@surveys_bp.route("/", methods=["POST"])
@swag_from({
    "tags": ["Surveys"],
    "responses": {
        201: {
            "description": "Survey created"
        }
    }
})
@researcher_required()
def create_survey():

    data = request.get_json()

    researcher_id = int(
        get_jwt_identity()
    )

    survey = Survey(
        title=data.get("title"),
        description=data.get("description"),
        researcher_id=researcher_id
    )

    db.session.add(survey)
    db.session.commit()

    log_event(
        researcher_id,
        f"created survey {survey.id}"
    )

    return jsonify({
        "message": "Survey created successfully",
        "survey_id": survey.id
    }), 201

@surveys_bp.route("/", methods=["GET"])
@swag_from({
    "tags": ["Surveys"],
    "responses": {
        200: {
            "description": "List surveys"
        }
    }
})
@jwt_required()
def get_surveys():

    claims = get_jwt()

    role = claims.get("role")

    user_id = int(
        get_jwt_identity()
    )

    # Admin voit tout

    if role == "admin":

        surveys = Survey.query.all()

    # Chercheur voit ses enquêtes

    elif role == "researcher":

        surveys = Survey.query.filter_by(
            researcher_id=user_id
        ).all()

    # Répondant voit seulement les enquêtes publiées
    # et non archivées

    else:

        surveys = Survey.query.filter(
            Survey.is_published == True,
            Survey.archived_at.is_(None)
        ).all()

    result = []

    for survey in surveys:

        result.append({

            "id": survey.id,
            "title": survey.title,
            "description": survey.description,
            "researcher_id": survey.researcher_id,
            "is_published": survey.is_published,
            "archived_at": survey.archived_at

        })

    return jsonify(result), 200

@surveys_bp.route("/<int:survey_id>", methods=["GET"])
@swag_from({
    "tags": ["Surveys"],
    "responses": {
        200: {
            "description": "Survey details"
        }
    }
})
@jwt_required()
def get_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({
            "message": "Survey not found"
        }), 404

    questions = []

    for question in survey.questions:

        questions.append({
            "id": question.id,
            "title": question.title,
            "type": question.type,
            "options": question.options
        })

    return jsonify({
        "id": survey.id,
        "title": survey.title,
        "description": survey.description,
        "researcher_id": survey.researcher_id,
        "is_published": survey.is_published,
        "archived_at": survey.archived_at,
        "questions": questions
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


@surveys_bp.route(
    "/<int:survey_id>/publish",
    methods=["POST"]
)

@swag_from({
    "tags": ["Surveys"],
    "responses": {
        200: {
            "description": "Survey published"
        }
    }
})
@jwt_required()
def publish_survey(survey_id):

    survey = Survey.query.get(
        survey_id
    )

    if not survey:

        return jsonify({
            "message": "Survey not found"
        }),404

    claims = get_jwt()

    role = claims.get("role")

    user_id = int(
        get_jwt_identity()
    )

    if role == "researcher":

        if survey.researcher_id != user_id:

            return jsonify({
                "message":
                "You can only publish your own surveys"
            }),403

    survey.is_published = True

    db.session.commit()

    log_event(
        user_id,
        f"published survey {survey.id}"
    )

    return jsonify({
        "message":
            "Survey published successfully"
    }), 200

@surveys_bp.route(
    "/<int:survey_id>/unpublish",
    methods=["POST"]
)
@jwt_required()
def unpublish_survey(survey_id):

    survey = Survey.query.get(
        survey_id
    )

    if not survey:

        return jsonify({
            "message":
            "Survey not found"
        }),404

    claims = get_jwt()

    role = claims.get("role")

    user_id = int(
        get_jwt_identity()
    )

    if role == "researcher":

        if survey.researcher_id != user_id:

            return jsonify({
                "message":
                "You can only unpublish your own surveys"
            }),403

    survey.is_published = False

    db.session.commit()

    return jsonify({
        "message":
        "Survey unpublished successfully"
    }),200


@swag_from({
    "tags": ["Surveys"],
    "responses": {
        200: {
            "description": "Survey archived"
        }
    }
})
@surveys_bp.route(
    "/<int:survey_id>/archive",
    methods=["PATCH"]
)
@researcher_required()
def archive_survey(survey_id):

    survey = Survey.query.get(
        survey_id
    )

    if not survey:
        return jsonify({
            "message": "Survey not found"
        }),404

    researcher_id = int(
        get_jwt_identity()
    )

    if survey.researcher_id != researcher_id:

        return jsonify({
            "message":
            "You can only archive your own survey"
        }),403

    survey.archived_at = datetime.utcnow()

    db.session.commit()

    log_event(
        researcher_id,
        f"archived survey {survey.id}"
    )

    return jsonify({
        "message":
            "Survey archived successfully"
    }), 200


@surveys_bp.route(
    "/<int:survey_id>/unarchive",
    methods=["PATCH"]
)
@researcher_required()
def unarchive_survey(survey_id):

    survey = Survey.query.get(
        survey_id
    )

    if not survey:
        return jsonify({
            "message": "Survey not found"
        }),404

    researcher_id = int(
        get_jwt_identity()
    )

    if survey.researcher_id != researcher_id:

        return jsonify({
            "message":
            "You can only unarchive your own survey"
        }),403

    survey.archived_at = None

    db.session.commit()

    return jsonify({
        "message":
        "Survey unarchived successfully"
    }),200


@surveys_bp.route(
    "/<int:survey_id>/export/csv",
    methods=["GET"]
)
@jwt_required()
def export_csv(survey_id):

    survey = Survey.query.get(
        survey_id
    )

    if not survey:

        return jsonify({
            "message":
            "Survey not found"
        }),404

    claims = get_jwt()

    role = claims.get("role")

    user_id = int(
        get_jwt_identity()
    )

    if role == "researcher":

        if survey.researcher_id != user_id:

            return jsonify({
                "message":
                "Unauthorized"
            }),403

    csv_file = generate_csv_export(
        survey_id
    )

    log_event(
        user_id,
        f"exported csv survey {survey.id}"
    )

    return send_file(
        BytesIO(
            csv_file.getvalue().encode("utf-8")
        ),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"survey_{survey_id}.csv"
    )


@surveys_bp.route(
    "/<int:survey_id>/export/excel",
    methods=["GET"]
)
@jwt_required()
def export_excel(survey_id):

    survey = Survey.query.get(
        survey_id
    )

    if not survey:

        return jsonify({
            "message":
            "Survey not found"
        }),404

    claims = get_jwt()

    role = claims.get("role")

    user_id = int(
        get_jwt_identity()
    )

    if role == "researcher":

        if survey.researcher_id != user_id:

            return jsonify({
                "message":
                "Unauthorized"
            }),403

    excel_file = generate_excel_export(
        survey_id
    )

    log_event(
        user_id,
        f"exported excel survey {survey.id}"
    )

    return send_file(
        excel_file,
        as_attachment=True,
        download_name=f"survey_{survey_id}.xlsx",
        mimetype=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )


@surveys_bp.route(
    "/my-participations",
    methods=["GET"]
)
@jwt_required()
def my_participations():

    user_id = int(
        get_jwt_identity()
    )

    answers = Answer.query.filter_by(
        user_id=user_id
    ).all()

    survey_ids = set()

    result = []

    for answer in answers:

        survey_id = (
            answer.question.survey_id
        )

        if survey_id in survey_ids:
            continue

        survey_ids.add(
            survey_id
        )

        survey = Survey.query.get(
            survey_id
        )

        result.append({

            "survey_id": survey.id,

            "title": survey.title,

            "answered_at":
                answer.created_at

        })

    return jsonify(result), 200



