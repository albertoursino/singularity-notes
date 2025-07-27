from datetime import datetime
import json
from pathlib import Path
import re
from time import time
from typing import Any

from loguru import logger
import yaml


def remove_empty_lines(lines: list[str]) -> list[str]:
    """Remove empty lines from a list of strings."""
    return [line for line in lines if line.strip()]


def setup_post():
    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    # Read the created article
    raw_post = Path(config.get("output_dir")) / "raw_post.md"
    with raw_post.open() as f:
        content = f.read()

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
**PDF Url**: {best_article_json["pdf_url"]}
"""

    # Create a new post in Hugo
    filename = f"post_{config.get('openai_model_name')}_{int(time())}.md"
    hugo_post = Path("app") / "content" / "posts" / filename
    with hugo_post.open("w") as f:
        f.write(header + "\n" + content + "\n\n" + credits)
        logger.success(f"Post successfully created at {str(hugo_post)!r}.")


if __name__ == "__main__":
    setup_post()
