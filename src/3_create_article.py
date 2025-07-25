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

with open("src/prompt_create_article.txt", "r") as file:
    prompt = file.read()

prompt += f"\n\n{text}"

num_tokens = len(prompt.split())
logger.debug(f"Number of tokens in the prompt: {num_tokens}")

client = OpenAI()
model = config.get("openai_model_name")
logger.info(f"Generating blog article from the best article PDF using {model!r}...")
response = client.responses.create(model=model, input=prompt)
markdown = response.output[0].content[0].text

output_file = Path(config.get("output_dir")) / "article.md"
with open(output_file, "w", encoding="utf-8") as md_file:
    md_file.write(markdown)
    logger.success(
        f"Blog article successfully generated and saved to {str(output_file)!r}."
    )
