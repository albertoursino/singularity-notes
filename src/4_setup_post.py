from datetime import datetime
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

filename = f"article_{config.get('openai_model_name')}_{int(time())}.md"

# Read the created article
article_source_filepath = Path(config.get("output_dir")) / "article.md"
with article_source_filepath.open() as f:
    content = f.read()

title, subtitle, content = extract_and_remove_title_subtitle(content)

header = f"""---
author: [Powered by ChatGPT (OpenAI)]
title: "{title}"
date: "{datetime.now().strftime("%Y-%m-%d")}"
description: "{subtitle}"
summary: "{subtitle}"
ShowToc: false
---
"""

# Create a new post in Hugo
article_dest_filepath = Path("app") / "content" / "posts" / filename
with article_dest_filepath.open("w") as f:
    f.write(header + "\n" + content)
