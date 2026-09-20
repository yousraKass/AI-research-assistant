import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# lazy import prompt loader to avoid import cycles if not present
try:
    from .prompt_loader import load_prompt
except Exception:
    load_prompt = None

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def _mock_summary(text: str, prompt: str = None) -> str:
    # I will make it more informative later on 
    return f"[MOCK SUMMARY] {text[:60]}..."
   


def summarize(text: str, prompt_template: str) -> str:
    """Summarize `text` using `prompt_template`.

    `prompt_template` can be either a literal prompt string or the name
    of a prompt file (without extension) located in `app/llm/prompts/`.
    If the environment variable `LLM_MODEL` is set to `mock`, this returns
    a deterministic local mock summary without making network requests.
    """
    model = os.getenv("LLM_MODEL", "")

    # If prompt_template is a prompt name, try to load it
    if load_prompt is not None:
        try:
            prompt_template = load_prompt(prompt_template, text=text)
        except FileNotFoundError:
            # treat prompt_template as literal
            pass

    # explicit mock mode
    if model == "mock":
        return _mock_summary(text, prompt_template)

    try:
        response = client.chat.completions.create(
            model=model or os.getenv("LLM_DEFAULT_MODEL"),
            messages=[
                {"role": "system", "content": prompt_template},
                {"role": "user", "content": text},
            ],
            max_tokens=2048,
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"LLM request failed: {e}")
        return _mock_summary(text, prompt_template)