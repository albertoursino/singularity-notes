from pathlib import Path


def create_output_dir(output_dir: Path) -> None:
    """Create the output directory if it does not exist."""
    if not output_dir.exists():
        output_dir.mkdir(parents=True)


def check_empty_line(line: str) -> bool:
    """Raise ValueError if the line is not empty."""
    if line.strip():
        raise ValueError("Expected an empty line.")
    return True


def validate_content(content: str) -> None:
    """Validate the content of the post."""
    if not content:
        raise ValueError("Content is empty.")

    lines = content.splitlines()

    if len(lines) < 11:
        raise ValueError("Content must have at least 10 lines.")

    if not lines[0].startswith("# "):
        raise ValueError("First line must be a title starting with '# '.")

    check_empty_line(lines[1])

    if not lines[2].startswith("Subtitle: "):
        raise ValueError("Third line must be a subtitle starting with 'Subtitle: '.")

    check_empty_line(lines[3])

    if not lines[4].strip() == "---":
        raise ValueError("Fourth line must be a separator '---'.")

    check_empty_line(lines[5])

    num_h3 = content.count("###")
    num_sep = content.count("---") - 1
    assert num_h3 == num_sep, (
        f"Number of '###' headers ({num_h3}) must match number of separators ('---') minus one ({num_sep})."
    )

    for i, line in enumerate(lines):
        if line.strip() == "###":
            if i == 0 or i == len(lines) - 1:
                raise ValueError("Separator '###' must have a space before and after.")
            if lines[i - 1].strip() != "":
                raise ValueError(
                    f"Line before separator '###' at line {i + 1} must be empty."
                )
            if lines[i + 1].strip() != "":
                raise ValueError(
                    f"Line after separator '###' at line {i + 1} must be empty."
                )

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if i == 0:
                raise ValueError("Separator '---' cannot be the first line.")
            if lines[i - 1].strip() != "":
                raise ValueError(
                    f"Line before separator '---' at line {i + 1} must be empty."
                )
