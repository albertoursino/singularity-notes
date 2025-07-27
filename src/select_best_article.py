import os
from pathlib import Path
import sys
from typing import Any
from loguru import logger
import requests
from dotenv import load_dotenv
from openai import OpenAI
import json
import yaml

from utils import create_output_dir

load_dotenv()


def select_best_article():
    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    try:
        with (Path(config.get("output_dir")) / "arxiv_articles.json").open() as f:
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
            f"Article {number}:\nTitle: {title}\nSummary: {summary}\n"
        )

    formatted_articles = "\n".join(article_summaries)

    if not config.get("debug"):
        # Prepare prompt
        with open("src/resources/prompt_select_best_article.txt", "r") as file:
            prompt = file.read()
        prompt += f"\n\n{formatted_articles}"
        logger.debug(f"Number of tokens in the prompt: {len(prompt.split())}")

        retries = 0
        while retries < 5:
            try:
                client = OpenAI()
                response = client.responses.create(
                    model=config.get("openai_model_name"), input=prompt
                )
                number = int(response.output[0].content[0].text)
            except Exception as e:
                logger.error(f"Error during OpenAI API call: {e}")
                retries += 1
                logger.info(f"Retrying... ({retries}/5)")
            else:
                break

        if retries == 5:
            logger.error("Failed to select the best article after 5 retries.")
            # TODO: send an email
            sys.exit(1)
    else:
        logger.info("Debug mode is enabled, skipping OpenAI API call...")
        number = 0

    # Get the PDF URL of the selected article
    pdf_url = None
    best_article_json = None
    for article in articles:
        if article.get("number") == number:
            best_article_json = article

            pdf_url = article.get("pdf_url")
            logger.debug(f"Selected article title: {article.get('title')}")

            article.pop("number")

            with (Path(config.get("output_dir")) / "best_article.json").open("w") as f:
                json.dump(article, f)

            break

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

    # Save the best article's PDF
    response = requests.get(pdf_url)
    if response.status_code == 200:
        output_file = Path(config.get("output_dir")) / "best_article.pdf"
        create_output_dir(Path(config.get("output_dir")))
        with open(output_file, "wb") as f:
            f.write(response.content)
            logger.success(f"Best article saved at {str(output_file)!r}")


if __name__ == "__main__":
    select_best_article()
