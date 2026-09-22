from app.llm.provider import get_langchain_chat_model


def test_get_langchain_chat_model_uses_openrouter_base_url(monkeypatch):
    monkeypatch.setenv('OPENROUTER_API_KEY', 'test-key')
    monkeypatch.setenv('LLM_MODEL', 'openai/gpt-4o-mini')

    model = get_langchain_chat_model()

    assert model is not None
    assert model.model_name == 'openai/gpt-4o-mini'
    assert model.openai_api_key.get_secret_value() == 'test-key'
    assert model.openai_api_base == 'https://openrouter.ai/api/v1'
