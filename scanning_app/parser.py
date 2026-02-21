import base64
import json
import logging

from .config import ALLOWED_EXTENSIONS, MIME_TYPES, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, SYSTEM_PROMPT


class ReceiptParseError(Exception):
    def __init__(self, error_code: str, message: str, http_status: int):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.http_status = http_status


class NotAReceiptError(Exception):
    pass


def get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def parse_receipt_image(image_bytes: bytes, ext: str, client) -> dict:
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    mime_type = MIME_TYPES[ext]

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Parse this grocery receipt and return the JSON.",
                        },
                    ],
                }
            ],
        )
    except Exception as e:
        print(e)
        raise ReceiptParseError(
            error_code="api_error",
            message="Receipt parsing service unavailable. Please try again.",
            http_status=500,
        ) from e

    raw_text = response.content[0].text.strip().strip("```json").strip("```")

    try:
        logging.info("response message : %s", raw_text)
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        logging.error(e)
        raise ReceiptParseError(
            error_code="parse_error",
            message="Could not parse receipt data.",
            http_status=500,
        ) from e

    if parsed.get("error") == "not_a_receipt":
        raise NotAReceiptError("Image does not contain a grocery receipt.")

    return parsed
