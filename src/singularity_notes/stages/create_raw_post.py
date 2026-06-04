import json
from pathlib import Path
import sys
import PyPDF2
from jsonschema import ValidationError
from loguru import logger
from jsonschema import validate

from singularity_notes import ARTICLE_SCHEMA, CREATE_POST_PROMPT


def create_raw_post(model: str, pdf_path: Path, max_retries: int = 5) -> dict:
    """Using an OpenAI LLM, creates an article given the original paper `best_article.pdf`.

    The output is saved as a JSON file `raw_post.json`. The model bases its decision on the content of the PDF, and the prompt `prompt_create_post.txt`.

    Args:
        model: The OpenAI model name to use for generation.
        pdf_path: The path to the PDF file.
        max_retries: The maximum number of retries in case of JSON validation failure.
    """
    # Get PDF content
    pdf_content = ""
    with pdf_path.open(mode="rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            pdf_content += page.extract_text() or ""

    # Construct the prompt
    with open(CREATE_POST_PROMPT, "r") as file:
        create_post_prompt = file.read()

    with Path(ARTICLE_SCHEMA).open() as f:
        article_schema = json.load(f)

    create_post_prompt += f"\n{pdf_content}\n\nOUTPUT:"

    retries = 0
    while retries < max_retries:
        try:
            logger.info(f"Generating response with model {model!r}...")
            # TODO: Use hugging face
            # model_output = OpenAI().responses.create(model=model, input=create_post_prompt).output_text
            logger.info(f"# Used tokens in input: {len(create_post_prompt.split())}")
            logger.info(f"# Used tokens in output: {len(model_output.split())}")
            model_output_dict: dict = json.load(model_output)
            logger.info("Validating the generated post against the schema...")
            validate(model_output_dict, article_schema)
        except ValidationError as e:
            logger.error(f"Schema validation failed: {e}")
            retries += 1
            logger.info(f"Retrying... ({retries}/{max_retries})")
        except Exception as e:
            logger.error(f"Error during OpenAI API call: {e}. Exiting...")
            sys.exit(1)
        else:
            logger.success("Post successfully generated")
            break
    if retries == max_retries:
        logger.error(f"Failed to create the post after {max_retries} retries.")
        sys.exit(1)

    return model_output_dict
