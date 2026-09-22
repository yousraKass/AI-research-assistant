from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

PROMPT_DIR = Path(__file__).parent / 'prompts'


def load_prompt_template(name: str) -> ChatPromptTemplate:
    """Load a prompt template as a reusable LangChain ChatPromptTemplate."""
    path = PROMPT_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")

    text = path.read_text(encoding='utf-8')
    return ChatPromptTemplate.from_template(text)
