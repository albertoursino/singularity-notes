from pathlib import Path
from singularity_notes.constants import Models
from singularity_notes.stages.create_raw_post import create_raw_post
from singularity_notes.stages.setup_post import setup_post


def main(model: Models, pdf_path: Path, max_retries: int, output_dir: Path) -> None:
    raw_post = create_raw_post(model=model, pdf_path=pdf_path, max_retries=max_retries)
    setup_post(model=model, raw_post=raw_post, output_dir=output_dir)


if __name__ == "__main__":
    main(
        model=Models.GPT_5_2_PRO.value,
        pdf_path=Path("output/best_article.pdf"),
        max_retries=1,
        output_dir=Path("output"),
    )
