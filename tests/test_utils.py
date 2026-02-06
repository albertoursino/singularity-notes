import json
from pathlib import Path
from typing import Any

from jsonschema import ValidationError
import pytest
from singularity_notes.utils import validate_json_data


DATA_FOLDER = Path("tests/data")


@pytest.fixture  # type: ignore
def article_schema() -> Any:
    with Path("src/singularity_notes/resources/article_schema.json").open() as f:
        return json.load(f)


def test_validate_json_data_good_post(article_schema: dict[Any, Any]) -> None:
    with (DATA_FOLDER / "good_post.json").open() as f:
        model_output = json.load(f)

    assert validate_json_data(model_output, article_schema)


def test_validate_json_data_empty_sections(article_schema: dict[Any, Any]) -> None:
    with (DATA_FOLDER / "empty_sections.json").open() as f:
        model_output = json.load(f)

    with pytest.raises(ValidationError):
        validate_json_data(model_output, article_schema)


def test_validate_json_data_empty_section_content(article_schema: dict[Any, Any]) -> None:
    with (DATA_FOLDER / "empty_section_content.json").open() as f:
        model_output = json.load(f)

    with pytest.raises(ValidationError):
        validate_json_data(model_output, article_schema)


def test_validate_json_data_empty_section_header(article_schema: dict[Any, Any]) -> None:
    with (DATA_FOLDER / "empty_section_header.json").open() as f:
        model_output = json.load(f)

    with pytest.raises(ValidationError):
        validate_json_data(model_output, article_schema)


def test_validate_json_data_empty_subtitle(article_schema: dict[Any, Any]) -> None:
    with (DATA_FOLDER / "empty_subtitle.json").open() as f:
        model_output = json.load(f)

    with pytest.raises(ValidationError):
        validate_json_data(model_output, article_schema)


def test_validate_json_data_empty_title(article_schema: dict[Any, Any]) -> None:
    with (DATA_FOLDER / "empty_title.json").open() as f:
        model_output = json.load(f)

    with pytest.raises(ValidationError):
        validate_json_data(model_output, article_schema)


def test_validate_json_data_missing_sections_property(
    article_schema: dict[Any, Any],
) -> None:
    with (DATA_FOLDER / "missing_sections_property.json").open() as f:
        model_output = json.load(f)

    with pytest.raises(ValidationError):
        validate_json_data(model_output, article_schema)


def test_validate_json_data_missing_subtitle_property(
    article_schema: dict[Any, Any],
) -> None:
    with (DATA_FOLDER / "missing_subtitle_property.json").open() as f:
        model_output = json.load(f)

    with pytest.raises(ValidationError):
        validate_json_data(model_output, article_schema)


def test_validate_json_data_missing_title_property(
    article_schema: dict[Any, Any],
) -> None:
    with (DATA_FOLDER / "missing_title_property.json").open() as f:
        model_output = json.load(f)

    with pytest.raises(ValidationError):
        validate_json_data(model_output, article_schema)
