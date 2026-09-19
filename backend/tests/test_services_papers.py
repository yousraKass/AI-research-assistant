import json
from unittest.mock import patch

from app.services import papers as papers_service


def test_search_normalizes_semantic_scholar(monkeypatch):
    sample = [
        {
            'paperId': 'abc123',
            'title': 'Test Paper',
            'abstract': 'An abstract',
            'authors': [{'name': 'Alice'}],
            'year': 2023,
            'citationCount': 5,
            'url': 'https://example.org/paper',
        }
    ]

    def fake_ss(query, limit=10):
        return [
            {
                'paperId': 'abc123',
                'title': 'Test Paper',
                'abstract': 'An abstract',
                'authors': [{'name': 'Alice'}],
                'year': 2023,
                'citationCount': 5,
                'url': 'https://example.org/paper',
            }
        ]

    monkeypatch.setattr('app.tools.semantic_scholar.search_papers', fake_ss)

    res = papers_service.search('test query', source='semantic_scholar', limit=1)
    assert res['query'] == 'test query'
    assert isinstance(res['results'], list)
    assert res['results'][0]['title'] == 'Test Paper'
    assert res['results'][0]['authors'] == ['Alice']
