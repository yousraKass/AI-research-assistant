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

    # Mock the current plain paper summary and structured synthesis paths.
    def fake_summarize(text, prompt_template):
        if prompt_template == 'paper_summarization':
            return f"Summary: {text[:30]}"
        return 'UNKNOWN'

    def fake_structured_synthesis(text, prompt_template, schema):
        return schema(
            common_findings='Both papers use method X and report improvements.',
            differences='Paper B reports a different evaluation metric yielding different magnitude.',
            limitations='Small datasets and limited ablation.'
        )

    monkeypatch.setattr('app.services.papers.search', fake_search)
    monkeypatch.setattr('app.llm.provider.summarize', fake_summarize)
    monkeypatch.setattr('app.llm.provider.summarize_structured', fake_structured_synthesis)

    res = research_service.research('some query', limit=2)
    assert res['research_question'] == 'some query'
    assert len(res['sources']) == 2
    assert len(res['paper_summaries']) == 2
    assert 'Both papers' in res['common_findings'] or res['common_findings']
    assert 'differences' in res or isinstance(res['differences'], str)


def test_research_uses_structured_synthesis_output(monkeypatch):
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
            }
        ],
    }

    monkeypatch.setattr('app.services.papers.search', lambda query, source='semantic_scholar', limit=10: fake_results)
    monkeypatch.setattr('app.llm.provider.summarize', lambda text, prompt_template: 'Summary: method X improved results.')

    def fake_structured(text, prompt_template, schema):
        return schema(
            common_findings='Shared method X improved results across papers.',
            differences='No major disagreement was observed.',
            limitations='Sample size remains limited.'
        )

    monkeypatch.setattr('app.llm.provider.summarize_structured', fake_structured)

    res = research_service.research('some query', limit=1)
    assert res['common_findings'] == 'Shared method X improved results across papers.'
    assert res['differences'] == 'No major disagreement was observed.'
    assert res['limitations'] == 'Sample size remains limited.'


def test_research_handles_empty_filtered_results(monkeypatch):
    monkeypatch.setattr(
        'app.services.papers.search',
        lambda query, source='semantic_scholar', limit=10: {'query': query, 'source': source, 'results': []}
    )

    res = research_service.research('empty', limit=3)
    assert res['research_question'] == 'empty'
    assert res['sources'] == []
    assert res['paper_summaries'] == []
    assert 'No relevant papers' in res['common_findings'] or res['common_findings'] == ''


def test_research_handles_structured_synthesis_failure(monkeypatch):
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
            }
        ],
    }

    monkeypatch.setattr('app.services.papers.search', lambda query, source='semantic_scholar', limit=10: fake_results)
    monkeypatch.setattr('app.llm.provider.summarize_structured', lambda text, prompt_template, schema: (_ for _ in ()).throw(RuntimeError('provider unavailable')))

    res = research_service.research('some query', limit=1)
    assert res['common_findings'] == ''
    assert res['differences'] == ''
    assert res['limitations'] == ''
