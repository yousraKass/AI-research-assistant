import os

from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - optional dependency path
    ChatPromptTemplate = None
    ChatOpenAI = None

try:
    from .prompt_loader import load_prompt_template
except Exception:  # pragma: no cover - optional dependency path
    load_prompt_template = None


class StructuredSummary(BaseModel):
    common_findings: str = ''
    differences: str = ''
    limitations: str = ''


def get_langchain_chat_model(model_name: str | None = None):
    """Return a LangChain ChatOpenAI configured for OpenRouter."""
    if ChatOpenAI is None:
        raise ImportError("langchain-openai is not installed")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is required for the LangChain OpenRouter client")

    resolved_model = model_name or os.getenv("LLM_MODEL") or os.getenv("LLM_DEFAULT_MODEL") or "openai/gpt-4o-mini"
    return ChatOpenAI(
        model=resolved_model,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2,
        max_tokens=2048,
    )


def _resolve_prompt_template(prompt_template):
    if isinstance(prompt_template, str):
        if load_prompt_template is not None:
            try:
                return load_prompt_template(prompt_template)
            except FileNotFoundError:
                pass
        if ChatPromptTemplate is not None:
            return ChatPromptTemplate.from_template(prompt_template)
        raise ValueError("No prompt template loader is available")

    if ChatPromptTemplate is not None and not hasattr(prompt_template, 'invoke'):
        return ChatPromptTemplate.from_template(str(prompt_template))

    return prompt_template


def _summarize_with_langchain(text: str, prompt_template) -> str:
    """Use a LangChain chat model to summarize the supplied text."""
    template = _resolve_prompt_template(prompt_template)
    model = get_langchain_chat_model()
    chain = template | model
    result = chain.invoke({"text": text})
    return result.content.strip()


def summarize_structured(text: str, prompt_template, schema: type[BaseModel] = StructuredSummary):
    """Use a LangChain model configured for Pydantic structured output."""
    template = _resolve_prompt_template(prompt_template)
    model = get_langchain_chat_model()
    structured_model = model.with_structured_output(schema)
    chain = template | structured_model
    result = chain.invoke({"text": text})

    if isinstance(result, dict):
        return schema(**result)
    if hasattr(result, 'model_dump'):
        return schema(**result.model_dump())
    return result


def _mock_summary(text: str, prompt: str = None) -> str:
    return f"[MOCK SUMMARY] {text[:60]}..."


def summarize(text: str, prompt_template) -> str:
    """Summarize `text` using the current LangChain-backed OpenRouter flow."""
    if os.getenv("LLM_MODEL", "").lower() == "mock":
        return _mock_summary(text, str(prompt_template))

    try:
        return _summarize_with_langchain(text, prompt_template)
    except Exception as exc:  # pragma: no cover - network/provider errors handled by a fallback
        print(f"LangChain request failed: {exc}")
        return _mock_summary(text, str(prompt_template))