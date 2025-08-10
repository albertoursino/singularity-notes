import os
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

sys.path.append(str(Path.cwd()))

from src.utils import create_output_dir

load_dotenv()


def select_best_article(config: dict):
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
            f"**Number**: {number}\n**Title**: {title}\n**Abstract**: {summary}\n"
        )

    formatted_articles = "\n".join(article_summaries)

    if not config["debug"]:
        # Construct prompt
        with open("src/resources/prompt_select_best_article.txt", "r") as file:
            prompt = file.read()
        prompt += f"\n\n{formatted_articles}\nRESPONSE:"

        retries = 0
        output_tokens = 0
        while retries < 5:
            try:
                client = OpenAI()
                votes_dict = {}
                for i in tqdm(
                    range(config["select_best_article"]["reasoning_paths"]),
                    desc="Select the best article...",
                ):
                    response = client.responses.create(
                        model=config["model"], input=prompt
                    )
                    try:
                        number = int(response.output[0].content[0].text)
                    except Exception:
                        continue
                    if number not in votes_dict:
                        votes_dict[number] = 1
                    else:
                        votes_dict[number] += 1

                # Get the most common answer
                number = max(votes_dict, key=votes_dict.get)

                output_tokens += len(response.output[0].content[0].text.split())
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

    logger.debug(f"# Votes to the best article: {votes_dict[number]}/{i + 1}")
    logger.debug(
        f"# Used tokens in input: {len(prompt.split()) * config['select_best_article']['reasoning_paths']}"
    )
    logger.debug(f"# Used tokens in output: {output_tokens}")

    # Get the PDF URL of the selected article
    pdf_url = None
    best_article_json = None
    for article in articles:
        if article.get("number") == number:
            best_article_json = article

            pdf_url = article.get("pdf_url")
            logger.debug(f"Best article title: {article.get('title')}")

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

    response = requests.get(pdf_url)
    if response.status_code == 200:
        # Save the best article's PDF
        pdf_file = Path(config["output_dir"]) / "best_article.pdf"
        with open(pdf_file, "wb") as f:
            f.write(response.content)
        logger.success(f"PDF of the best research paper saved at {str(pdf_file)!r}")

        # Save PDF content for debugging purposes
        pdf_content = ""
        with (pdf_file).open(mode="rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                pdf_content += page.extract_text() or ""

        txt_file = Path(config["output_dir"]) / "best_article.txt"
        with (txt_file).open(mode="w") as f:
            f.write(pdf_content)
        logger.success(f"Raw content of the PDF saved at {str(txt_file)!r}")


if __name__ == "__main__":
    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    create_output_dir(Path(config.get("output_dir")))

    select_best_article(config)
