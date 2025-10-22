from pathlib import Path
from typing import Any
from loguru import logger
import yaml

from src.stages.create_raw_post import create_raw_post
from src.stages.get_arxiv_articles import get_arxiv_articles
from src.stages.select_best_article import select_best_article
from src.stages.setup_post import setup_post
from src.utils import create_output_dir


OUTPUT_DIR: Path = Path("output/")
CONFIG_FILE: Path = Path("config.yaml")


class ArticleProcessor:
    def __init__(self, config: dict, output_dir: Path):
        self.config = config
        self.output_dir = output_dir

    def get_arxiv_articles(self):
        get_arxiv_articles(self.config, self.output_dir)

    def select_best_article(self):
        select_best_article(self.config, self.output_dir)

    def create_raw_post(self):
        create_raw_post(self.config, self.output_dir)

    def setup_post(self):
        setup_post(self.config, self.output_dir)

    def run(self):
        logger.info("Fetching articles from arXiv...")
        self.get_arxiv_articles()
        logger.info("Selecting the best article...")
        self.select_best_article()
        logger.info("Creating raw post...")
        self.create_raw_post()
        logger.info("Setting up Hugo post...")
        self.setup_post()


if __name__ == "__main__":
    with open(CONFIG_FILE, "r") as f:
        config: dict[str, Any] = yaml.safe_load(f)

    processor = ArticleProcessor(config, create_output_dir(OUTPUT_DIR))
    processor.run()
