import json
from pathlib import Path
from typing import Any

from jsonschema import ValidationError
import pytest
from jsonschema import validate


@pytest.fixture
def article_schema() -> Any:
    """Loads the article schema used in production."""
    with Path("src/singularity_notes/resources/article_schema.json").open() as f:
        return json.load(f)


@pytest.mark.parametrize(
    "filename",
    ["tests/data/valid_json/1.json"],
)
def test_validate_valid_json(article_schema: dict[Any, Any], filename: str) -> None:
    with Path(filename).open() as f:
        model_output = json.load(f)

    validate(model_output, article_schema)


@pytest.mark.parametrize(
    "filename",
    [
        "tests/data/invalid_json/empty_sections.json",
        "tests/data/invalid_json/empty_section_content.json",
        "tests/data/invalid_json/empty_section_header.json",
        "tests/data/invalid_json/empty_subtitle.json",
        "tests/data/invalid_json/empty_title.json",
        "tests/data/invalid_json/missing_sections_property.json",
        "tests/data/invalid_json/missing_subtitle_property.json",
        "tests/data/invalid_json/missing_title_property.json",
    ],
)
def test_validate_invalid_json(article_schema: dict[Any, Any], filename: str) -> None:
    with Path(filename).open() as f:
        model_output = json.load(f)

    with pytest.raises(ValidationError):
        validate(model_output, article_schema)
