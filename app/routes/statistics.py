from flasgger import swag_from
from flask import Blueprint, jsonify, request

from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from app.services.statistics_service import generate_statistics
from app.models.survey import Survey


statistics_bp = Blueprint(
    "statistics",
    __name__,
    url_prefix="/surveys"
)

@swag_from({
    "tags": ["Statistics"],
    "responses": {
        200: {
            "description": "Survey statistics"
        }
    }
})
@statistics_bp.route(
    "/<int:survey_id>/statistics",
    methods=["GET"]
)
@jwt_required()
def survey_statistics(survey_id):

    claims = get_jwt()
    role = claims.get("role")
    gender = request.args.get("gender")
    age_group = request.args.get("age_group")
    date = request.args.get("date")

    if role not in [
        "admin",
        "researcher"
    ]:

        return jsonify({
            "message":
            "Access denied"
        }),403


    survey = Survey.query.get(
        survey_id
    )


    if not survey:

        return jsonify({
            "message":
            "Survey not found"
        }),404

    user_id = int(
        get_jwt_identity()
    )

    if role == "researcher":

        if survey.researcher_id != user_id:
            return jsonify({
                "message":
                    "You can only access your own survey statistics"
            }), 403

    data = generate_statistics(
        survey_id=survey_id,
        gender=gender,
        age_group=age_group,
        date=date
    )

    return jsonify({

        "survey_id": survey.id,
        "title": survey.title,
        "statistics": data

    }),200

