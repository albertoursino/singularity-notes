from typing import Any
from loguru import logger
import yaml
from src.get_arxiv_articles import get_arxiv_articles
from src.select_best_article import select_best_article
from src.create_article import create_article
from src.setup_post import setup_post
import os

if __name__ == "__main__":
    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    os.makedirs(config.get("output_dir"), exist_ok=True)

    logger.info("Fetching articles from arXiv...")
    get_arxiv_articles()
    logger.info("Selecting the best article...")
    select_best_article()
    logger.info("Creating article...")
    create_article()
    logger.info("Setting up post...")
    setup_post()
    logger.success("Pipeline completed successfully.")
