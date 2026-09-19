from pathlib import Path

PROMPT_DIR = Path(__file__).parent / 'prompts'


def load_prompt(name: str, **kwargs) -> str:
    """Load a prompt by name from the prompts directory and format it.

    Example: load_prompt('paper_summarization', title='...', text='...')
    """
    path = PROMPT_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    text = path.read_text(encoding='utf-8')
    try:
        return text.format(**kwargs)
    except Exception:
        # If formatting fails, return raw text (caller may handle substitution)
        return text
