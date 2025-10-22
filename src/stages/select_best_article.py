from pathlib import Path
import sys
from typing import Any
import PyPDF2
from loguru import logger
import requests
from dotenv import load_dotenv
from openai import OpenAI
import json
from tqdm import tqdm
import yaml

from src.utils import UsedArticles

load_dotenv()


def select_best_article(config: dict[Any, Any], output_dir: Path) -> None:
    try:
        with (output_dir / "arxiv_articles.json").open() as f:
            articles = json.load(f)
    except FileNotFoundError:
        logger.error("No articles found. Please run the pipeline to fetch articles.")
        sys.exit(1)

    article_summaries = []
    for article in articles:
        number = article.get("number")
        title = article.get("title")
        summary = article.get("summary")
        article_summaries.append(
            f"**Number**: {number}\n**Title**: {title}\n**Abstract**: {summary}\n"
        )

    formatted_articles = "\n".join(article_summaries)

    if not config["debug"]:
        # Construct prompt
        with open("src/resources/prompt_select_best_article.txt", "r") as file:
            prompt = file.read()
        prompt += f"\n\n{formatted_articles}\nOUTPUT:"

        retries = 0
        output_tokens = 0
        while retries < config["max_retries"]:
            try:
                client = OpenAI()
                votes_dict: dict[int, int] = {}
                for i in tqdm(
                    range(config["reasoning_paths"]),
                    desc=f"Select the best article with model {config['model']!r}...",
                ):
                    response = client.responses.create(
                        model=config["model"], input=prompt
                    )
                    number = int(response.output_text)

                    if number not in votes_dict:
                        votes_dict[number] = 1
                    else:
                        votes_dict[number] += 1

                # Get the most common answer
                number = max(votes_dict, key=lambda x: votes_dict.get(x, 0))

                output_tokens += len(response.output_text.split())
            except Exception as e:
                logger.error(f"Error during OpenAI API call: {e}. Exiting...")
                sys.exit(-1)
            else:
                break
        if retries == config["max_retries"]:
            logger.error(
                f"Failed to select the best article after {config['max_retries']} retries."
            )
            # TODO: send an email
            sys.exit(1)

        logger.debug(f"# Votes to the best article: {votes_dict[number]}/{i + 1}")
        logger.debug(
            f"# Used tokens in input: {len(prompt.split()) * config['reasoning_paths']}"
        )
        logger.debug(f"# Used tokens in output: {output_tokens}")
    else:
        logger.info("Debug mode is enabled, skipping OpenAI API call...")
        number = 0

    # Get the PDF URL of the selected article
    pdf_url = ""
    for article in articles:
        if article.get("number") == number:
            pdf_url = article.get("pdf_url")
            logger.debug(f"Best article title: {article.get('title')}")

            article.pop("number")

            # Save best article in a JSON file
            with (output_dir / "best_article.json").open("w") as f:
                json.dump(article, f)

            break

    response = requests.get(pdf_url)
    if response.status_code == 200:
        # Save the best article's PDF
        pdf_file = output_dir / "best_article.pdf"
        with open(pdf_file, "wb") as f:
            f.write(response.content)
        logger.success(f"PDF of the best research paper saved at {str(pdf_file)!r}")

        # Save PDF content for debugging purposes
        pdf_content = ""
        with (pdf_file).open(mode="rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                pdf_content += page.extract_text() or ""

        txt_file = output_dir / "best_article.txt"
        with (txt_file).open(mode="w") as f:
            f.write(pdf_content)
        logger.success(f"Raw content of the PDF saved at {str(txt_file)!r}")
    else:
        logger.error(f"Can't fetch the URL {pdf_url!r}.")
        with (output_dir / "best_article.json").open("r") as f:
            best_article_json = json.load(f)
        # * We can't use this article so we consider it used
        UsedArticles().update_used_articles(best_article_json)
        # TODO: send signal to re-run the pipeline
        sys.exit(1)


if __name__ == "__main__":
    sys.path.append(str(Path.cwd()))
    from run_pipeline import OUTPUT_DIR
    from src.utils import create_output_dir

    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    select_best_article(config, create_output_dir(OUTPUT_DIR))
