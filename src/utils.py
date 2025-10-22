import json
import os
from pathlib import Path
from typing import Any
from jsonschema import validate
from loguru import logger


def create_output_dir(output_dir: Path) -> Path:
    """Create the output directory if it does not exist."""
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    return output_dir


def validate_json_data(data: dict[Any, Any], schema: dict[Any, Any]) -> bool:
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


def update_used_articles(used_articles_path: Path, best_article_json: dict) -> None:
    """If it exits, updates the JSON file at `used_articles_path` with a new entry `best_article_json`."""
    # Update used articles if the file exists
    if used_articles_path.exists():
        with used_articles_path.open("r") as f:
            used_articles: list[dict] = json.load(f)

        used_articles.append(best_article_json)

        with used_articles_path.open("w") as f:
            json.dump(used_articles, f, indent=2)
        logger.success(
            f"Used articles updated successfully at {str(used_articles_path)!r}"
        )
    else:
        logger.success(
            f"The file {str(used_articles_path)!r} does not exist. Update failed"
        )
