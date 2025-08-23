from pathlib import Path
import sys
from typing import Any
from loguru import logger
import yaml


OUTPUT_DIR = Path("output/")

if __name__ == "__main__":
    from src.stages.select_best_article import select_best_article
    from src.stages.create_raw_post import create_raw_post
    from src.stages.setup_post import setup_post
    from src.stages.get_arxiv_articles import get_arxiv_articles
    from src.utils import create_output_dir

    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    create_output_dir(OUTPUT_DIR)

    try:
        logger.info("Fetching articles from arXiv...")
        get_arxiv_articles(config)
        logger.info("Selecting the best article...")
        select_best_article(config)
        logger.info("Creating article...")
        create_raw_post(config)
        logger.info("Setting up post...")
        setup_post(config)
        logger.success("Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        # TODO: send an email
        sys.exit(1)
