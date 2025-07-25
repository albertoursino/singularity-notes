from pathlib import Path
from typing import Any
import arxiv
import json

from loguru import logger
import yaml

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

# Fetch and format results
results = []
for i, paper in enumerate(client.results(search)):
    results.append(
        {
            "number": i,
            "title": paper.title,
            "authors": ", ".join(author.name for author in paper.authors),
            "published": paper.published.strftime("%Y-%m-%d"),
            "summary": paper.summary,
            "pdf_url": paper.pdf_url,
        }
    )

# Save results to a JSON file
output_file = Path(config.get("output_dir")) / "arxiv_articles.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
    logger.success(
        f"JSON file with {len(results)} articles saved successfully at {str(output_file)!r}"
    )
