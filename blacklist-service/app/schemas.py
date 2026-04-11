from marshmallow import ValidationError, fields, post_load, pre_load, validate

from app import ma


class BlacklistEntrySchema(ma.Schema):
    email = fields.Email(
        required=True,
        error_messages={"required": "El campo email es obligatorio."},
    )
    app_uuid = fields.UUID(
        required=True,
        error_messages={"required": "El campo app_uuid es obligatorio."},
    )
    blocked_reason = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(
            max=255,
            error="El campo blocked_reason no puede superar los 255 caracteres.",
        ),
    )

    @pre_load
    def normalize_input(self, data, **kwargs):
        if not isinstance(data, dict):
            raise ValidationError("El cuerpo de la solicitud debe ser un JSON válido.")

        normalized_data = dict(data)

        email = normalized_data.get("email")
        if isinstance(email, str):
            normalized_data["email"] = email.strip().lower()

        blocked_reason = normalized_data.get("blocked_reason")
        if isinstance(blocked_reason, str):
            stripped_reason = blocked_reason.strip()
            normalized_data["blocked_reason"] = stripped_reason or None

        return normalized_data

    @post_load
    def normalize_output(self, data, **kwargs):
        if "app_uuid" in data:
            data["app_uuid"] = str(data["app_uuid"])

        return data


blacklist_entry_schema = BlacklistEntrySchema()
