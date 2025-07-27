from datetime import datetime
import json
from pathlib import Path
import re
from time import time
from typing import Any

import yaml


def extract_and_remove_title_subtitle(content):
    title_pattern = (
        r"^# (\S+\s+.+\S)$"  # Matches '# <emoji> <title>' capturing emoji and title
    )
    subtitle_pattern = r"^\*\*Subtitle:\*\*\s+(.+)$"  # Matches '**Subtitle:** <text>'
    separator_pattern = r"^-{3,}\n"  # Matches '---' or more dashes followed by newline

    # Extract title (including emoji)
    title_match = re.search(title_pattern, content, re.MULTILINE)
    title = title_match.group(1) if title_match else ""

    # Extract subtitle
    subtitle_match = re.search(subtitle_pattern, content, re.MULTILINE)
    subtitle = subtitle_match.group(1) if subtitle_match else ""

    # Remove title, subtitle, and the first --- after subtitle
    if title_match:
        content = re.sub(title_pattern, "", content, count=1, flags=re.MULTILINE)
    if subtitle_match:
        content = re.sub(subtitle_pattern, "", content, count=1, flags=re.MULTILINE)
        # Remove the first --- after subtitle
        content = re.sub(separator_pattern, "", content, count=1, flags=re.MULTILINE)

    # Clean up extra blank lines or spaces
    content = content.strip()
    return title, subtitle, content


with open("config.yaml", "r") as config_file:
    config: dict[str, Any] = yaml.safe_load(config_file)


# Read the created article
raw_post = Path(config.get("output_dir")) / "raw_post.md"
with raw_post.open() as f:
    content = f.read()

title, subtitle, content = extract_and_remove_title_subtitle(content)

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
