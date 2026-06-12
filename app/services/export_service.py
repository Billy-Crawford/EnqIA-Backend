import csv
from io import StringIO
from io import BytesIO
from openpyxl import Workbook

from app.models.question import Question


def generate_csv_export(survey_id):

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Respondent ID",
        "Question ID",
        "Question",
        "Answer"
    ])

    questions = Question.query.filter_by(
        survey_id=survey_id
    ).all()

    for question in questions:

        for answer in question.answers:

            # choix multiple
            if question.type == "multiple_choice":

                values = [
                    option.option_value
                    for option in answer.options
                ]

                answer_value = ", ".join(values)

            else:

                answer_value = answer.value

            writer.writerow([
                answer.user_id,
                question.id,
                question.title,
                answer_value
            ])

    output.seek(0)

    return output


def generate_excel_export(survey_id):

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = "Survey Results"

    sheet.append([
        "Respondent ID",
        "Question ID",
        "Question",
        "Answer"
    ])

    questions = Question.query.filter_by(
        survey_id=survey_id
    ).all()

    for question in questions:

        for answer in question.answers:

            if question.type == "multiple_choice":

                values = [
                    option.option_value
                    for option in answer.options
                ]

                answer_value = ", ".join(values)

            else:

                answer_value = answer.value

            sheet.append([
                answer.user_id,
                question.id,
                question.title,
                answer_value
            ])

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    return output



