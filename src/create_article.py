from pathlib import Path
from typing import Any
import PyPDF2
from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI
import yaml

load_dotenv()

with open("config.yaml", "r") as config_file:
    config: dict[str, Any] = yaml.safe_load(config_file)

if not config.get("debug"):
    pdf_path = Path(config.get("output_dir")) / "best_article.pdf"
else:
    pdf_path = Path(config.get("output_dir")) / "dummy_astronomy_article.pdf"

text = ""

with pdf_path.open(mode="rb") as file:
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""

# Now 'text' contains the entire PDF content as a string
prompt = (
    f"You are a science journalist writing for an astronomy blog aimed at curious readers with no technical background.\n\
    Your task is to write a clear, engaging blog article (around 2 to 5 minutes of reading time) summarizing the paper's most important findings.\n\n\
    Follow these guidelines:\n\
    - Write in Markdown format\n\
    - Use a friendly, accessible tone\n\
    - Explain complex ideas using analogies or simple language\n\
    - Highlight why the discovery or topic matters\n\
    - Keep it concise: focus on the key message and interesting insights\n\
    - Include a catchy title, a subtitle, and clear section headings with emojis\n\
    - Make the blog post enjoyable to read while staying faithful to the paper's intent\n\
    - Avoid citing the authors of the paper\n\
    - Avoid technical jargon unless absolutely necessary, and explain it when used\n\n\
    Use consistent punctuation throughout:\n\
    - If using em dashes (—), include spaces (e.g. 'hello — world')\n\
    - If using straight quotes, not curly quotes (“ ”)\n\
    - Prefer periods and commas as needed, but avoid mixing styles.\n\
    - Use emojis frequently!\n\n\
    Here is the research paper content:\n\
    {text}"
)

num_tokens = len(prompt.split())
logger.debug(f"Number of tokens in the prompt: {num_tokens}")

client = OpenAI()
model = "gpt-4.1-nano"
logger.info(f"Generating blog article from the best article PDF using {model!r}...")
response = client.responses.create(model=model, input=prompt)
markdown = response.output[0].content[0].text

output_file = Path(config.get("output_dir")) / "article.md"
with open(output_file, "w", encoding="utf-8") as md_file:
    md_file.write(markdown)
    logger.success(
        f"Blog article successfully generated and saved to {str(output_file)!r}."
    )
