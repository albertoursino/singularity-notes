from datetime import datetime
from pathlib import Path
from time import time

from loguru import logger


def setup_post(model: str, raw_post: dict, output_dir: Path) -> None:
    """Using the content of `raw_post`, creates and saves a new markdown post at `output_dir`.

    Args:
        model: The model used to generate the post.
        raw_post: The content of the raw post.
        output_dir: Directory where the output files will be saved.
    """
    title = raw_post["title"]
    subtitle = raw_post["subtitle"]
    sections = raw_post["sections"]

    logger.debug(f"Title of the article: {title}")
    logger.debug(f"Subtitle of the article: {subtitle}")
    logger.debug(f"Number of sections: {len(sections)}")

    # Setup content
    content = ""
    for section in sections:
        section_header = section["header"]
        section_content = section["content"]
        content += "### " + section_header + "\n\n" + section_content + "\n\n" + "---" + "\n\n"

    # Create header
    header = (
        f"""---\nauthor: [Powered by OpenAI ({model})]\ntitle: "{title}"\n"""
        f"""date: "{datetime.now().strftime("%Y-%m-%d")}"\ndescription: "{subtitle}"\n"""
        f"""summary: "{subtitle}"\nShowToc: false\n---\n\n"""
    )

    # Create a new post in Hugo
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    post = output_dir / f"post_{int(time())}.md"
    with post.open("w") as f:
        f.write(header + content + credits)
        logger.success(f"Post successfully created at {str(post)!r}.")
