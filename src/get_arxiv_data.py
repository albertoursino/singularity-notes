import arxiv
import json

# Initialize the arXiv client
client = arxiv.Client()

MAX_RESULTS = 10

# Search for the 10 most recent articles in the astrophysics category
search = arxiv.Search(
    query="cat:astro-ph*",
    max_results=MAX_RESULTS,
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
with open("arxiv_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
