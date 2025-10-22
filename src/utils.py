import json
import os
from pathlib import Path
from typing import Any
from jsonschema import validate


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


class UsedArticles:
    def __init__(self):
        self.used_articles_path = Path("used_articles.json")
        self._create_file()

    def get_used_articles(self):
        with open(self.used_articles_path, "r", encoding="utf-8") as f:
            used_articles = json.load(f)
        return {article["arxiv_id"] for article in used_articles}

    def _create_file(self) -> None:
        """Creates the file if it doesn't exist."""
        if not os.path.exists(self.used_articles_path):
            with open(self.used_articles_path, "w") as f:
                f.write("[]")

    def update_used_articles(self, best_article_json: dict) -> None:
        if self.used_articles_path.exists():
            with self.used_articles_path.open("r") as f:
                used_articles: list[dict] = json.load(f)

            used_articles.append(best_article_json)

            with self.used_articles_path.open("w") as f:
                json.dump(used_articles, f, indent=2)
        else:
            # TODO: raise error
            pass
