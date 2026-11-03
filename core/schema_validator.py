"""
core/schema_validator.py — JSON schema validation for extraction output.
"""
import json
import os
from typing import Tuple, List

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'output_schema.json')


def load_schema() -> dict:
    """Load the JSON output schema."""
    schema_path = os.path.normpath(SCHEMA_PATH)
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_output(data: dict) -> Tuple[bool, List[str]]:
    """
    Validate a parsed invoice dict against the output schema.
    Returns (is_valid, list_of_errors).
    """
    if not HAS_JSONSCHEMA:
        return True, ["jsonschema not installed — schema validation skipped"]
    try:
        schema = load_schema()
        validator = jsonschema.Draft202012Validator(schema)
        errors = list(validator.iter_errors(data))
        if errors:
            msgs = [f"{e.json_path}: {e.message}" for e in errors]
            return False, msgs
        return True, []
    except Exception as e:
        return False, [str(e)]
