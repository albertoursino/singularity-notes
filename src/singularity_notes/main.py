from pathlib import Path
from typing import Any
from singularity_notes.stages.create_raw_post import create_raw_post
from singularity_notes.stages.get_arxiv_articles import get_arxiv_articles
from singularity_notes.stages.select_best_article import select_best_article
from singularity_notes.stages.setup_post import setup_post
from singularity_notes.utils import create_output_dir
import yaml  # type: ignore[import-untyped]


OUTPUT_DIR: Path = Path("output/")


if __name__ == "__main__":
    with Path("config.yaml").open() as f:
        config: dict[str, Any] = yaml.safe_load(f)

    get_arxiv_articles(num_articles=int(config["number_of_articles"]), output_dir=create_output_dir(OUTPUT_DIR))
    select_best_article(model=config["model"], output_dir=create_output_dir(OUTPUT_DIR))
    create_raw_post(model=config["model"], output_dir=create_output_dir(OUTPUT_DIR), max_retries=int(config["max_retries"]))
    setup_post(model=config["model"], output_dir=create_output_dir(OUTPUT_DIR))
