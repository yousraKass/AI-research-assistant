import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


def summarize(text: str, prompt_template: str) -> str:
    try:
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL"),
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
        return (
            "[MOCK SUMMARY]\n\n"
            "This is a fallback summary because the LLM service "
            "was unavailable.\n\n"
            f"The provided text contains approximately {len(text.split())} words "
            "and could not be summarized by the configured LLM, this mock summary is for testing purposes only."
        )