from datetime import datetime, timezone

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import BlacklistEntry
from app.schemas import blacklist_entry_schema


class BlacklistResource(Resource):
    method_decorators = [jwt_required()]

    def post(self):
        payload = request.get_json(silent=True) or {}

        try:
            validated_data = blacklist_entry_schema.load(payload)
        except ValidationError as validation_error:
            errors = validation_error.messages
            if isinstance(errors, list):
                errors = {"_schema": errors}
            return {"message": "Datos inválidos", "errors": errors}, 400

        existing_entry = BlacklistEntry.query.filter_by(
            email=validated_data["email"]
        ).first()
        if existing_entry:
            return {"message": "El email ya se encuentra en la blacklist"}, 409

        request_ip = _extract_request_ip()

        blacklist_entry = BlacklistEntry(
            email=validated_data["email"],
            app_uuid=validated_data["app_uuid"],
            blocked_reason=validated_data.get("blocked_reason"),
            request_ip=request_ip,
            created_at=datetime.now(timezone.utc),
        )

        db.session.add(blacklist_entry)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "El email ya se encuentra en la blacklist"}, 409

        return {"message": "Email agregado exitosamente a la blacklist"}, 201


def _extract_request_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", "").strip()
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.remote_addr or "0.0.0.0"
