
from datetime import datetime

from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask import send_file
from io import BytesIO

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt
)

from app.extensions.db import db
from app.models.answer import Answer
from app.models.survey import Survey
from app.decorators.roles import roles_required

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

# =========================================================
# CREATE SURVEY
# =========================================================
@surveys_bp.route("/", methods=["POST"])
@roles_required(["admin", "researcher"])
def create_survey():

    data = request.get_json()

    user_id = int(get_jwt_identity())

    survey = Survey(
        title=data.get("title"),
        description=data.get("description"),
        researcher_id=user_id
    )

    db.session.add(survey)
    db.session.commit()

    log_event(user_id, f"created survey {survey.id}")

    return jsonify({
        "message": "Survey created successfully",
        "survey_id": survey.id
    }), 201


# =========================================================
# GET ALL SURVEYS
# =========================================================
@surveys_bp.route("/", methods=["GET"])
@jwt_required()
def get_surveys():

    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    if role == "admin":
        surveys = Survey.query.all()

    elif role == "researcher":
        surveys = Survey.query.filter_by(researcher_id=user_id).all()

    else:
        surveys = Survey.query.filter(
            Survey.is_published == True,
            Survey.archived_at.is_(None)
        ).all()

    return jsonify([
        {
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "researcher_id": s.researcher_id,
            "is_published": s.is_published,
            "archived_at": s.archived_at
        }
        for s in surveys
    ]), 200


# =========================================================
# GET ONE SURVEY
# =========================================================
@surveys_bp.route("/<int:survey_id>", methods=["GET"])
@jwt_required()
def get_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    return jsonify({
        "id": survey.id,
        "title": survey.title,
        "description": survey.description,
        "researcher_id": survey.researcher_id,
        "is_published": survey.is_published,
        "archived_at": survey.archived_at,
        "questions": [
            {
                "id": q.id,
                "title": q.title,
                "type": q.type,
                "options": q.options
            }
            for q in survey.questions
        ]
    }), 200


# =========================================================
# UPDATE SURVEY (ADMIN FIX INCLUDED)
# =========================================================
@surveys_bp.route("/<int:survey_id>", methods=["PUT"])
@roles_required(["admin", "researcher"])
def update_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    # 🔥 IMPORTANT FIX
    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    data = request.get_json()

    survey.title = data.get("title", survey.title)
    survey.description = data.get("description", survey.description)

    db.session.commit()

    return jsonify({"message": "Survey updated successfully"}), 200


# =========================================================
# DELETE SURVEY (ADMIN FIX INCLUDED)
# =========================================================
@surveys_bp.route("/<int:survey_id>", methods=["DELETE"])
@roles_required(["admin", "researcher"])
def delete_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    db.session.delete(survey)
    db.session.commit()

    return jsonify({"message": "Survey deleted successfully"}), 200


# =========================================================
# PUBLISH
# =========================================================
@surveys_bp.route("/<int:survey_id>/publish", methods=["POST"])
@roles_required(["admin", "researcher"])
def publish_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    survey.is_published = True
    db.session.commit()

    log_event(user_id, f"published survey {survey.id}")

    return jsonify({"message": "Survey published"}), 200


# =========================================================
# UNPUBLISH
# =========================================================
@surveys_bp.route("/<int:survey_id>/unpublish", methods=["POST"])
@roles_required(["admin", "researcher"])
def unpublish_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    survey.is_published = False
    db.session.commit()

    return jsonify({"message": "Survey unpublished"}), 200


# =========================================================
# ARCHIVE
# =========================================================
@surveys_bp.route("/<int:survey_id>/archive", methods=["PATCH"])
@roles_required(["admin", "researcher"])
def archive_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    survey.archived_at = datetime.utcnow()
    db.session.commit()

    log_event(user_id, f"archived survey {survey.id}")

    return jsonify({"message": "Survey archived"}), 200


# =========================================================
# UNARCHIVE
# =========================================================
@surveys_bp.route("/<int:survey_id>/unarchive", methods=["PATCH"])
@roles_required(["admin", "researcher"])
def unarchive_survey(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    survey.archived_at = None
    db.session.commit()

    return jsonify({"message": "Survey unarchived"}), 200


# =========================================================
# EXPORT CSV
# =========================================================
@surveys_bp.route("/<int:survey_id>/export/csv", methods=["GET"])
@jwt_required()
def export_csv(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    csv_file = generate_csv_export(survey_id)

    log_event(user_id, f"exported csv survey {survey.id}")

    return send_file(
        BytesIO(csv_file.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"survey_{survey_id}.csv"
    )


# =========================================================
# EXPORT EXCEL
# =========================================================
@surveys_bp.route("/<int:survey_id>/export/excel", methods=["GET"])
@jwt_required()
def export_excel(survey_id):

    survey = Survey.query.get(survey_id)

    if not survey:
        return jsonify({"message": "Survey not found"}), 404

    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    if role != "admin" and survey.researcher_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    excel_file = generate_excel_export(survey_id)

    log_event(user_id, f"exported excel survey {survey.id}")

    return send_file(
        excel_file,
        as_attachment=True,
        download_name=f"survey_{survey_id}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =========================================================
# MY PARTICIPATIONS
# =========================================================
@surveys_bp.route("/my-participations", methods=["GET"])
@jwt_required()
def my_participations():

    user_id = int(get_jwt_identity())

    answers = Answer.query.filter_by(user_id=user_id).all()

    seen = set()
    result = []

    for a in answers:
        survey_id = a.question.survey_id

        if survey_id in seen:
            continue

        seen.add(survey_id)

        survey = Survey.query.get(survey_id)

        result.append({
            "survey_id": survey.id,
            "title": survey.title,
            "answered_at": a.created_at
        })

    return jsonify(result), 200

