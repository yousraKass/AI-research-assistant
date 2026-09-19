import json
from unittest.mock import patch

from app.services import research as research_service


def test_research_summarization_and_synthesis(monkeypatch):
    # Create fake papers returned by services.papers.search
    fake_results = {
        'query': 'q',
        'source': 'semantic_scholar',
        'results': [
            {
                'title': 'Paper A',
                'abstract': 'Abstract A about method X and result Y.',
                'authors': ['Alice'],
                'year': 2022,
                'url': 'http://a',
            },
            {
                'title': 'Paper B',
                'abstract': 'Abstract B about method X and different result Z.',
                'authors': ['Bob'],
                'year': 2023,
                'url': 'http://b',
            },
        ],
    }

    def fake_search(query, source='semantic_scholar', limit=10):
        return fake_results

    # Mock provider.summarize to return short summaries for abstracts and a JSON synth
    def fake_summarize(text, prompt_template):
        if prompt_template == 'paper_summarization':
            return f"Summary: {text[:30]}"
        if prompt_template == 'synthesis_prompt':
            return json.dumps({
                'common_findings': 'Both papers use method X and report improvements.',
                'differences': 'Paper B reports a different evaluation metric yielding different magnitude.',
                'limitations': 'Small datasets and limited ablation.'
            })
        return 'UNKNOWN'

    monkeypatch.setattr('app.services.papers.search', fake_search)
    monkeypatch.setattr('app.llm.provider.summarize', fake_summarize)

    res = research_service.research('some query', limit=2)
    assert res['research_question'] == 'some query'
    assert len(res['sources']) == 2
    assert len(res['paper_summaries']) == 2
    assert 'Both papers' in res['common_findings'] or res['common_findings']
    assert 'differences' in res or isinstance(res['differences'], str)
