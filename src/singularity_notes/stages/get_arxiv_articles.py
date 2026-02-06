from pathlib import Path
import sys
from typing import Any
import arxiv
import json

from loguru import logger
import yaml  # type: ignore[import-untyped]

from utils import UsedArticles


def get_arxiv_articles(config: dict[Any, Any], output_dir: Path) -> None:
    # Initialize the arXiv client
    client = arxiv.Client()

    # Search for the 10 most recent articles in the astrophysics category
    search = arxiv.Search(
        query="cat:astro-ph*",
        max_results=config.get("number_of_articles"),
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Ascending,
    )

    used_arxiv_ids = UsedArticles().get_used_articles()

    # Fetch and format results
    results = []
    i = 0
    for paper in client.results(search):
        arxiv_id = paper.get_short_id()
        if arxiv_id in used_arxiv_ids:
            logger.warning(f"Skipping already used article: {arxiv_id}")
            continue
        results.append(
            {
                "number": i,
                "title": paper.title,
                "authors": ", ".join(author.name for author in paper.authors),
                "published": paper.published.strftime("%Y-%m-%d"),
                "summary": paper.summary,
                "pdf_url": paper.pdf_url,
                "arxiv_id": arxiv_id,
            }
        )
        i += 1

    # Save results to a JSON file
    output_file = output_dir / "arxiv_articles.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        logger.success(f"JSON file with {len(results)} articles saved successfully at {str(output_file)!r}")


if __name__ == "__main__":
    sys.path.append(str(Path.cwd()))
    from src.singularity_notes.main import OUTPUT_DIR
    from src.utils import create_output_dir

    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    get_arxiv_articles(config, create_output_dir(OUTPUT_DIR))
