from datetime import datetime
import json
import os
from pathlib import Path
import sys
from time import time
from typing import Any

from loguru import logger
import yaml


def setup_post(config: dict[Any, Any], output_dir: Path) -> None:
    # Read the created article from the JSON file
    try:
        raw_post = output_dir / "raw_post.json"
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
    with (output_dir / "best_article.json").open("r") as f:
        best_article_json = json.load(f)

    credits = (
        f"""**Source Paper's Authors**: {best_article_json["authors"]}\n\n"""
        f"""**PDF**: {best_article_json["pdf_url"]}"""
    )

    # Create a new post in Hugo
    posts_dir = Path("app") / "content" / "posts"
    Path(posts_dir).mkdir(parents=True, exist_ok=True)
    hugo_post = posts_dir / f"article_{int(time())}.md"
    with hugo_post.open("w") as f:
        f.write(header + content + credits)
        logger.success(f"Post successfully created at {str(hugo_post)!r}.")

    used_articles_path = Path("used_articles.json")

    # Update used articles if the file exists
    if os.path.exists(used_articles_path):
        with used_articles_path.open("r") as f:
            used_articles = json.load(f)

        used_articles.append(best_article_json)

        with used_articles_path.open("w") as f:
            json.dump(used_articles, f, indent=2)

        logger.success(
            f"Used articles updated successfully at {str(used_articles_path)!r}"
        )


if __name__ == "__main__":
    sys.path.append(str(Path.cwd()))
    from run_pipeline import OUTPUT_DIR
    from src.utils import create_output_dir

    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    setup_post(config, create_output_dir(OUTPUT_DIR))
