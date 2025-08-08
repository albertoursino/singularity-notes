from pathlib import Path
import sys
from typing import Any
import PyPDF2
from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI
import yaml

from utils import create_output_dir

load_dotenv()


def create_article():
    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    if config["debug"]:
        logger.info("Debug mode is enabled, skipping OpenAI API call...")
        markdown = """# This is a dummy title for testing purposes.

Subtitle: This is a dummy subtitle for testing purposes.

---

### This is a dummy section header for testing purposes.

This is a dummy paragraph for testing purposes. It will be replaced with the actual content generated from the best article PDF.

---
"""
    else:
        # Get PDF content
        pdf_content = ""
        with (Path(config["output_dir"]) / "best_article.pdf").open(mode="rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                pdf_content += page.extract_text() or ""

        # Construct the prompt
        with open("src/resources/prompt_create_article.txt", "r") as file:
            prompt = file.read()

        prompt += f"\n{pdf_content}\n\nRESPONSE:"

        try:
            client = OpenAI()
            model = config["openai_model_name"]
            logger.info(f"Generating blog article using {model!r}...")
            response = client.responses.create(model=model, input=prompt)
            markdown = response.output[0].content[0].text
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            # TODO: send an email
            sys.exit(1)

    logger.debug(f"# Used tokens in input: {len(prompt.split())}")
    logger.debug(f"# Used tokens in output: {len(markdown.split())}")

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
