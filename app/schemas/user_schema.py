from marshmallow import Schema, fields, validate


class UserRegisterSchema(Schema):

    firstname = fields.String(
        required=True
    )

    lastname = fields.String(
        required=True
    )

    email = fields.Email(
        required=True
    )

    password = fields.String(
        required=True,
        validate=validate.Length(min=6)
    )

    role = fields.String(
        required=True,
        validate=validate.OneOf(
            ["researcher", "respondent"]
        )
    )


