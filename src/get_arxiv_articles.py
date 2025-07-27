from pathlib import Path
from typing import Any
import arxiv
import json

from loguru import logger
import yaml


def get_arxiv_articles():
    # Initialize the arXiv client
    client = arxiv.Client()

    with open("config.yaml", "r") as config_file:
        config: dict[str, Any] = yaml.safe_load(config_file)

    # Search for the 10 most recent articles in the astrophysics category
    search = arxiv.Search(
        query="cat:astro-ph*",
        max_results=config.get("number_of_articles"),
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    # Get used articles
    used_articles_file = Path("used_articles.json")
    with open(used_articles_file, "r", encoding="utf-8") as f:
        used_articles = json.load(f)
    used_arxiv_ids = {article["arxiv_id"] for article in used_articles}

    # Fetch and format results
    results = []
    i = 0
    for paper in client.results(search):
        arxiv_id = paper.get_short_id()
        if arxiv_id in used_arxiv_ids:
            logger.warning(f"Skipping already used article: {arxiv_id}")
            if i != 0:
                i -= 1
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
    output_file = Path(config.get("output_dir")) / "arxiv_articles.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        logger.success(
            f"JSON file with {len(results)} articles saved successfully at {str(output_file)!r}"
        )


if __name__ == "__main__":
    get_arxiv_articles()
