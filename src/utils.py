from pathlib import Path
from jsonschema import validate


def create_output_dir(output_dir: Path) -> None:
    """Create the output directory if it does not exist."""
    if not output_dir.exists():
        output_dir.mkdir(parents=True)


def validate_json_data(data: dict, schema: dict) -> bool:
    """
    Validate JSON data against the provided JSON Schema.

    Args:
        data: The JSON object to validate.
        schema: The JSON Schema to validate against.

    Raises:
        jsonschema.exceptions.ValidationError: If the data don't respect the schema.

    Returns:
        bool: True if valid, raises otherwise.
    """
    validate(instance=data, schema=schema)
    return True
