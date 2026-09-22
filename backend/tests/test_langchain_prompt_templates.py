from app.llm.prompt_loader import load_prompt_template


def test_load_prompt_template_returns_langchain_template():
    template = load_prompt_template('paper_summarization')
    assert template is not None
    rendered = template.invoke({'text': 'Paper about transformers'})
    assert 'transformers' in rendered.to_string()
