import json
from pathlib import Path
import sys
from typing import Any
import PyPDF2
from dotenv import load_dotenv
from jsonschema import ValidationError
from loguru import logger
from jsonschema import validate
from openai import OpenAI
from singularity_notes.utils import create_output_dir
import yaml  # type: ignore[import-untyped]

load_dotenv()


def create_raw_post(model: str, output_dir: Path, max_retries: int = 5) -> None:
    """Using an OpenAI LLM, creates an article given the original paper `best_article.pdf`.

    The output is saved as a JSON file `raw_post.json`. The model bases its decision on the content of the PDF, and the prompt `prompt_create_post.txt`.

    Args:
        model: The OpenAI model name to use for generation.
        max_retries: The maximum number of retries in case of JSON validation failure.
        output_dir: The directory where the output JSON file will be saved.
    """
    # Get PDF content
    pdf_content = ""
    with (output_dir / "best_article.pdf").open(mode="rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            pdf_content += page.extract_text() or ""

    # Construct the prompt
    with open("src/singularity_notes/resources/prompt_create_post.txt", "r") as file:
        prompt = file.read()

    with Path("src/singularity_notes/resources/article_schema.json").open() as f:
        json_schema = json.load(f)

    prompt += f"\n{pdf_content}\n\nOUTPUT:"

    retries = 0
    while retries < max_retries:
        try:
            logger.info(f"Generating response with model {model!r}...")
            response = OpenAI().responses.create(model=model, input=prompt)

            model_output = response.output_text

            # Save the raw post in the output directory as a JSON file
            output_file = output_dir / "raw_post.json"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(model_output)
            logger.debug(f"Model output saved at {str(output_file)!r}")

            # Validate the JSON file
            logger.info("Validating JSON response...")
            with (output_file).open() as f:
                validate(json.load(f), json_schema)

        except ValidationError as e:
            logger.error(f"Schema validation failed: {e}")
            retries += 1
            logger.info(f"Retrying... ({retries}/{max_retries})")
        except Exception as e:
            logger.error(f"Error during OpenAI API call: {e}. Exiting...")
            sys.exit(1)
        else:
            logger.success(f"Post successfully generated and saved to {str(output_file)!r}.")
            break
    if retries == max_retries:
        logger.error(f"Failed to create the post after {max_retries} retries.")
        sys.exit(1)

    logger.debug(f"# Used tokens in input: {len(prompt.split())}")
    logger.debug(f"# Used tokens in output: {len(model_output.split())}")


if __name__ == "__main__":
    from singularity_notes.main import OUTPUT_DIR

    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    create_raw_post(model=config["model"], max_retries=config["max_retries"], output_dir=create_output_dir(OUTPUT_DIR))
