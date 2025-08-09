import sys
from loguru import logger
from src.stages.get_arxiv_articles import get_arxiv_articles
from src.stages.select_best_article import select_best_article
from src.stages.create_article import create_article
from src.stages.setup_post import setup_post

if __name__ == "__main__":
    try:
        logger.info("Fetching articles from arXiv...")
        get_arxiv_articles()
        logger.info("Selecting the best article...")
        select_best_article()
        logger.info("Creating article...")
        create_article()
        logger.info("Setting up post...")
        setup_post()
        logger.success("Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        # TODO: send an email
        sys.exit(1)
