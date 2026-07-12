from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "Prompts"


def load_prompt(name: str) -> str:
    """
    Загружает текстовый промпт из папки Prompts.
    Например:
        load_prompt("translator")
        -> Prompts/translator.txt
    """

    file_path = PROMPTS_DIR / f"{name}.txt"

    if not file_path.exists():
        raise FileNotFoundError(f"Промпт не найден: {file_path}")

    return file_path.read_text(encoding="utf-8").strip()