import json

from app.tools.search_tools import (
    get_paper,
    search_arxiv,
    search_semantic_scholar,
    search_web,
)


class _FakeResponse:
    def __init__(self, payload=None, text=''):
        self._payload = payload or {}
        self._text = text

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload

    @property
    def text(self):
        return self._text


def test_search_tools_are_independent(monkeypatch):
    def fake_get(url, **kwargs):
        params = kwargs.get('params') or {}
        if 'api.semanticscholar.org' in url:
            if url.endswith('/paper/search'):
                return _FakeResponse({
                    'data': [{
                        'paperId': 'ss-1',
                        'title': 'Semantic paper',
                        'abstract': 'Semantic abstract',
                        'authors': [{'name': 'Ada'}],
                        'year': 2024,
                        'citationCount': 10,
                        'url': 'https://example.org/semantic',
                    }]
                })
            return _FakeResponse({
                'title': 'Paper details',
                'abstract': 'Detailed abstract',
                'authors': [{'name': 'Ada Lovelace'}],
                'year': 2024,
                'url': 'https://example.org/paper',
            })
        if 'export.arxiv.org' in url:
            return _FakeResponse(
                text='''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Arxiv paper</title><summary>Arxiv abstract</summary><published>2024-01-01</published><author><name>Ada</name></author><id>http://arxiv.org/abs/2401.0001v1</id><link type="text/html" href="https://arxiv.org/abs/2401.0001v1" /></entry></feed>'''
            )
        if 'duckduckgo.com/html' in url:
            return _FakeResponse(
                text='''<html><body><a rel="nofollow" class="result-link" href="https://example.org/result">Example result</a></body></html>'''
            )
        raise AssertionError(f'unexpected url: {url}, params={params}')

    monkeypatch.setattr('httpx.get', fake_get)

    semantic = search_semantic_scholar.invoke({"query": 'llm reasoning', "limit": 1})
    arxiv = search_arxiv.invoke({"query": 'llm reasoning', "limit": 1})
    web = search_web.invoke({"query": 'llm reasoning', "limit": 1})
    paper = get_paper.invoke({"paper_id": 'ss-1'})

    assert semantic[0]['title'] == 'Semantic paper'
    assert arxiv[0]['title'] == 'Arxiv paper'
    assert web[0]['title'] == 'Example result'
    assert paper['title'] == 'Paper details'
