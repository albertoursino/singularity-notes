from datetime import datetime
import json
from pathlib import Path
import sys
from time import time
from typing import Any

from loguru import logger
import yaml

sys.path.append(str(Path.cwd()))

from src.utils import create_output_dir


def setup_post(config: dict):
    # Read the created article from the JSON file
    try:
        raw_post = Path(config.get("output_dir")) / "raw_post.json"
        with raw_post.open() as f:
            json_content = json.load(f)
    except FileNotFoundError:
        logger.error(f"Raw post file not found at {str(raw_post)!r}.")
        sys.exit(1)

    title = json_content["title"]
    subtitle = json_content["subtitle"]
    sections = json_content["sections"]

    logger.debug(f"Title of the article: {title}")
    logger.debug(f"Subtitle of the article: {subtitle}")
    logger.debug(f"Number of sections: {len(sections)}")

    # Setup content
    content = ""
    for section in sections:
        section_header = section["header"]
        section_content = section["content"]
        content += (
            "### " + section_header + "\n\n" + section_content + "\n\n" + "---" + "\n\n"
        )

    # Build Hugo header
    header = (
        f"""---\nauthor: [Powered by OpenAI ({config["model"]})]\ntitle: "{title}"\n"""
        f"""date: "{datetime.now().strftime("%Y-%m-%d")}"\ndescription: "{subtitle}"\n"""
        f"""summary: "{subtitle}"\nShowToc: false\n---\n\n"""
    )

    # Write credits
    with (Path(config.get("output_dir")) / "best_article.json").open("r") as f:
        best_article_json = json.load(f)

    credits = (
        f"""**Source Paper's Authors**: {best_article_json["authors"]}\n\n"""
        f"""**PDF**: {best_article_json["pdf_url"]}"""
    )

    # Create a new post in Hugo
    filename = f"article_{int(time())}.md"
    hugo_post = Path("app") / "content" / "posts" / filename
    with hugo_post.open("w") as f:
        f.write(header + content + credits)
        logger.success(f"Post successfully created at {str(hugo_post)!r}.")


if __name__ == "__main__":
    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    create_output_dir(Path(config.get("output_dir")))

    setup_post(config)
