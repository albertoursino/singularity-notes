import json
from pathlib import Path
import sys
from typing import Any
import PyPDF2
from dotenv import load_dotenv
from jsonschema import ValidationError
from loguru import logger
from openai import OpenAI
import yaml

sys.path.append(str(Path.cwd()))
from src.utils import validate_json_data

load_dotenv()


def create_raw_post(config: dict[Any, Any], output_dir: Path) -> None:
    output_file = output_dir / "raw_post.json"

    if config["debug"]:
        logger.info("Debug mode is enabled, skipping OpenAI API call...")
        model_output = """{
            "title": "🌌 Unveiling The Secrets Of Blazing Cosmic Behemoths: How The SST-1M Telescope Is Sherpherding Our Understanding Of Markarian 421",
            "subtitle": "Cutting-edge observations shed light on one of the universe's most energetic and enigmatic objects",
            "sections": [
                {
                    "header": "🔭 What Is So Special About Mrk 421?",
                    "content": "Imagine a lighthouse, but instead of shining on a coast..."
                },
                {
                    "header": "🛰️ How Did The New Observations Happen?",
                    "content": "Detecting gamma rays from Earth is tricky—these..."
                }
            ]
        }
        """
        # Save the raw post in the output directory as a JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(model_output)
        logger.debug(f"Model output saved at {str(output_file)!r}")
    else:
        # Get PDF content
        pdf_content = ""
        with (output_dir / "best_article.pdf").open(mode="rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                pdf_content += page.extract_text() or ""

        # Construct the prompt
        with open("src/resources/prompt_create_post.txt", "r") as file:
            prompt = file.read()

        with Path("src/resources/article_schema.json").open() as f:
            json_schema = json.load(f)

        prompt += f"\n{pdf_content}\n\nOUTPUT:"

        retries = 0
        while retries < config["max_retries"]:
            try:
                client = OpenAI()
                model = config["model"]

                logger.info(f"Generating response with model {model!r}...")
                response = client.responses.create(model=model, input=prompt)

                model_output = response.output_text

                # Save the raw post in the output directory as a JSON file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(model_output)
                logger.debug(f"Model output saved at {str(output_file)!r}")

                # Validate the JSON file
                logger.info("Validating JSON response...")
                with (output_file).open() as f:
                    validate_json_data(json.load(f), json_schema)

            except ValidationError as e:
                logger.error(f"Schema validation failed: {e}")
                retries += 1
                logger.info(f"Retrying... ({retries}/5)")
            except Exception as e:
                logger.error(f"Error during OpenAI API call: {e}. Exiting...")
                sys.exit(1)
            else:
                logger.success(
                    f"Post successfully generated and saved to {str(output_file)!r}."
                )
                break
        if retries == config["max_retries"]:
            logger.error(
                f"Failed to create the post after {config['max_retries']} retries."
            )
            # TODO: send an email
            sys.exit(1)

        logger.debug(f"# Used tokens in input: {len(prompt.split())}")
        logger.debug(f"# Used tokens in output: {len(model_output.split())}")


if __name__ == "__main__":
    sys.path.append(str(Path.cwd()))
    from run_pipeline import OUTPUT_DIR
    from src.utils import create_output_dir

    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    create_raw_post(config, create_output_dir(OUTPUT_DIR))
