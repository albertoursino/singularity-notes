from pathlib import Path
import sys
from typing import Any
import PyPDF2
from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI
import yaml

from src.utils import create_output_dir

load_dotenv()


def create_article():
    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    if config.get("debug"):
        logger.info("Debug mode is enabled, skipping OpenAI API call...")
        markdown = """# This is a dummy title for testing purposes.

Subtitle: This is a dummy subtitle for testing purposes.

---

### This is a dummy section header for testing purposes.

This is a dummy paragraph for testing purposes. It will be replaced with the actual content generated from the best article PDF.

---
"""
    else:
        with open("src/resources/prompt_create_article.txt", "r") as file:
            prompt = file.read()

        with open("src/resources/post_template.txt", "r") as file:
            post_template = file.read()

        prompt += "\n\nThe following is the structure of the final Markdown file that you have to fill out. "
        prompt += "Fill out **only** the parts in between '<>'. **Don't modify the other parts for any reason, leave as they are!**. "
        prompt += f"Double check that the last two rows are an empty row and then a row with '---'.\n{post_template}"

        pdf_path = Path(config.get("output_dir")) / "best_article.pdf"
        pdf_content = ""

        with pdf_path.open(mode="rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                pdf_content += page.extract_text() or ""

        prompt += f"\n\nHere is the research paper:\n\n{pdf_content}"

        num_tokens = len(prompt.split())
        logger.debug(f"Number of tokens in the prompt: {num_tokens}")

        try:
            client = OpenAI()
            model = config.get("openai_model_name")
            logger.info(
                f"Generating blog article from the best article PDF using {model!r}..."
            )
            response = client.responses.create(model=model, input=prompt)
            markdown = response.output[0].content[0].text
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            # TODO: send an email
            sys.exit(1)

    # Save the raw post in the output directory
    output_file = Path(config.get("output_dir")) / "raw_post.md"
    create_output_dir(Path(config.get("output_dir")))
    with open(output_file, "w", encoding="utf-8") as md_file:
        md_file.write(markdown)
        logger.success(
            f"Blog article successfully generated and saved to {str(output_file)!r}."
        )


if __name__ == "__main__":
    create_article()
