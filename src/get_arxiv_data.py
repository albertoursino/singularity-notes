import arxiv

# Initialize the arXiv client
client = arxiv.Client()

# Search for the 10 most recent articles in the astrophysics category
search = arxiv.Search(
    query="cat:astro-ph*",
    max_results=2,
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
            # "authors": ", ".join(author.name for author in paper.authors),
            # "published": paper.published.strftime("%Y-%m-%d"),
            "summary": paper.summary,
            # "id": paper.entry_id.split("/")[-1],
            # "pdf_url": paper.pdf_url,
        }
    )

# Output results in markdown format
markdown_output = "# 10 Most Recent Astronomy Papers from arXiv\n\n"
for i, paper in enumerate(results, 1):
    markdown_output += f"## {i}. {paper['title']}\n"
    markdown_output += f"- **Number**: {paper['number']}\n"
    # markdown_output += f"- **Authors**: {paper['authors']}\n"
    # markdown_output += f"- **Published**: {paper['published']}\n"
    # markdown_output += f"- **arXiv ID**: {paper['id']}\n"
    # markdown_output += f"- **PDF URL**: {paper['pdf_url']}\n\n"
    markdown_output += f"- **Abstract**: {paper['summary']}\n\n"

# Optionally, save to a markdown file
with open("recent_astronomy_papers.md", "w", encoding="utf-8") as f:
    f.write(markdown_output)
