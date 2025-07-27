from datetime import datetime
import json
from pathlib import Path
import re
from time import time
from typing import Any

from loguru import logger
import yaml


def check_empty_line(line: str) -> bool:
    """Raise ValueError if the line is not empty."""
    if line.strip():
        raise ValueError("Expected an empty line.")
    return True


def validate_content(content: str) -> None:
    """Validate the content of the post."""
    if not content:
        raise ValueError("Content is empty.")

    lines = content.splitlines()

    if len(lines) < 11:
        raise ValueError("Content must have at least 10 lines.")

    if not lines[0].startswith("# "):
        raise ValueError("First line must be a title starting with '# '.")

    check_empty_line(lines[1])

    if not lines[2].startswith("Subtitle: "):
        raise ValueError("Third line must be a subtitle starting with 'Subtitle: '.")

    check_empty_line(lines[3])

    if not lines[4].strip() == "---":
        raise ValueError("Fourth line must be a separator '---'.")

    check_empty_line(lines[5])

    num_h3 = content.count("###")
    num_sep = content.count("---") - 1
    assert num_h3 == num_sep, (
        f"Number of '###' headers ({num_h3}) must match number of separators ('---') minus one ({num_sep})."
    )

    for i, line in enumerate(lines):
        if line.strip() == "###":
            if i == 0 or i == len(lines) - 1:
                raise ValueError("Separator '###' must have a space before and after.")
            if lines[i - 1].strip() != "":
                raise ValueError(
                    f"Line before separator '###' at line {i + 1} must be empty."
                )
            if lines[i + 1].strip() != "":
                raise ValueError(
                    f"Line after separator '###' at line {i + 1} must be empty."
                )

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if i == 0:
                raise ValueError("Separator '---' cannot be the first line.")
            if lines[i - 1].strip() != "":
                raise ValueError(
                    f"Line before separator '---' at line {i + 1} must be empty."
                )


def setup_post():
    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    # Read the created article
    raw_post = Path(config.get("output_dir")) / "raw_post.md"
    with raw_post.open() as f:
        content = f.read()

    validate_content(content)
    logger.success("Content validation passed")

    lines = content.splitlines()

    # Extract and remove title (first line starting with "# ")
    title_match = re.match(r"# (.+)", lines[0])
    title = title_match.group(1).strip() if title_match else ""
    lines.pop(0)  # Remove the title line
    lines.pop(0)  # Remove empty line after title
    logger.debug(f"Extracted title: {title}")

    # Extract and remove subtitle (third line, starting with "Subtitle: ")
    if lines[0].startswith("Subtitle: "):
        subtitle = lines[0].replace("Subtitle: ", "", 1).strip()
    lines.pop(0)  # Remove the subtitle line
    lines.pop(0)  # Remove empty line after subtitle
    lines.pop(0)  # Remove the separator line
    lines.pop(0)  # Remove empty line after separator
    logger.debug(f"Extracted subtitle: {subtitle}")

    # Reconstruct content
    content = "\n".join(lines)

    # Build Hugo header
    header = f"""---
author: [Powered by ChatGPT (OpenAI)]
title: "{title}"
date: "{datetime.now().strftime("%Y-%m-%d")}"
description: "{subtitle}"
summary: "{subtitle}"
ShowToc: false
---
"""

    # Write credits
    with (Path(config.get("output_dir")) / "best_article.json").open("r") as f:
        best_article_json = json.load(f)

    credits = f"""**Source Paper's Authors**: {best_article_json["authors"]}\n
**PDF**: {best_article_json["pdf_url"]}
"""

    # Create a new post in Hugo
    filename = f"{int(time())}.md"
    hugo_post = Path("app") / "content" / "posts" / filename
    with hugo_post.open("w") as f:
        f.write(header + "\n" + content + "\n\n" + credits)
        logger.success(f"Post successfully created at {str(hugo_post)!r}.")


if __name__ == "__main__":
    setup_post()
