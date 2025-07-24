from pathlib import Path
from loguru import logger
import requests
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI
import json
import yaml

load_dotenv()

with open("config.yaml", "r") as config_file:
    config: dict = yaml.safe_load(config_file)

with open("arxiv_results.json", "r") as f:
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

    prompt = f"You are an editor of an astronomy newsletter for curious, non-expert readers.\
                Your task is to read them and choose only one that would be most interesting to publish (I will give you the task of summarizing the whole content of the selected paper) as today's featured article.\
                You must give me only the article 'number'. Imagine your only possible output is one single integer.\
                Focus on papers that are: 1. Easy to explain or make understandable 2. Related to exciting discoveries, space missions, telescopes, or cosmic phenomena\
                3. Likely to engage curious readers (e.g., black holes, exoplanets, new data from space).\n\n{formatted_articles}"

    num_tokens = len(prompt.split())
    logger.debug(f"Number of tokens in a single prompt: {num_tokens}")
    logger.debug(
        f"Number of tokens used to select the best article: {num_tokens * config.get('number_of_analyses')}"
    )

    dict = {}
    for i in tqdm(range(config.get("number_of_analyses"))):
        response = client.responses.create(model="gpt-4.1-nano", input=prompt)
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
        break

# Get content of the PDF
response = requests.get(pdf_url)
if response.status_code == 200:
    pdf_path = Path("best_article.pdf")
    with open(pdf_path, "wb") as f:
        f.write(response.content)
        logger.success(f"Best article saved at {str(pdf_path)!r}")
