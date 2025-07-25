from pathlib import Path
from typing import Any
from loguru import logger
import requests
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI
import json
import yaml

load_dotenv()


with open("config.yaml", "r") as config_file:
    config: dict[str, Any] = yaml.safe_load(config_file)

with (Path(config.get("output_dir")) / "arxiv_articles.json").open() as f:
    articles = json.load(f)

article_summaries = []
for article in articles:
    number = article.get("number", "N/A")
    title = article.get("title", "No Title")
    summary = article.get("summary", "No Summary")
    article_summaries.append(f"Article {number}:\nTitle: {title}\nSummary: {summary}\n")

formatted_articles = "\n".join(article_summaries)


if not config.get("debug"):
    client = OpenAI()

    with open("src/prompt_select_best_article.txt", "r") as file:
        prompt = file.read()

    prompt += f"\n\n{formatted_articles}"

    num_tokens = len(prompt.split())
    logger.debug(f"Number of tokens in a single prompt: {num_tokens}")
    logger.debug(
        f"Number of tokens used to select the best article: {num_tokens * config.get('number_of_analyses')}"
    )

    dict = {}
    for i in tqdm(range(config.get("number_of_analyses"))):
        response = client.responses.create(
            model=config.get("openai_model_name"), input=prompt
        )
        try:
            number = int(response.output[0].content[0].text)
        except Exception:
            continue
        if number not in dict:
            dict[number] = 1
        else:
            dict[number] += 1

    number = max(dict, key=dict.get)
else:
    number = 0


pdf_url = None
for article in articles:
    if article.get("number") == number:
        pdf_url = article.get("pdf_url")
        logger.debug(f"Selected article title: {article.get('title')}")

        with (Path(config.get("output_dir")) / "best_article.json").open("w") as f:
            json.dump(article, f)

        break

# Get content of the PDF
response = requests.get(pdf_url)
if response.status_code == 200:
    output_file = Path(config.get("output_dir")) / "best_article.pdf"
    with open(output_file, "wb") as f:
        f.write(response.content)
        logger.success(f"Best article saved at {str(output_file)!r}")
