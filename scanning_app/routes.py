from anthropic import Anthropic
from flask import Blueprint, current_app, jsonify, request

from .config import ALLOWED_EXTENSIONS
from .parser import NotAReceiptError, ReceiptParseError, get_extension, parse_receipt_image

bp = Blueprint("main", __name__)


def _get_client():
    return current_app.config.get("ANTHROPIC_CLIENT") or Anthropic()


@bp.route("/parse-receipt", methods=["POST"])
def parse_receipt():
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "no_file",
            "message": "No file was included in the request.",
        }), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({
            "success": False,
            "error": "no_file",
            "message": "No file was included in the request.",
        }), 400

    ext = get_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({
            "success": False,
            "error": "invalid_file_type",
            "message": f"Unsupported file type '{ext}'. Accepted: {', '.join(sorted(ALLOWED_EXTENSIONS))}.",
        }), 400

    image_bytes = file.read()
    if not image_bytes:
        return jsonify({
            "success": False,
            "error": "empty_file",
            "message": "The uploaded file appears to be empty.",
        }), 400

    try:
        parsed = parse_receipt_image(image_bytes, ext, _get_client())
    except NotAReceiptError:
        return jsonify({
            "success": False,
            "error": "not_a_receipt",
            "message": "Could not identify a grocery receipt in the provided image.",
        }), 422
    except ReceiptParseError as e:
        return jsonify({
            "success": False,
            "error": e.error_code,
            "message": e.message,
        }), e.http_status

    parsed["success"] = True
    return jsonify(parsed), 200


@bp.route("/")
def hello_world():
    return "Hello World"
