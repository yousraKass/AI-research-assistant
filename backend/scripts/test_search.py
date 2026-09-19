"""Quick script to test paper search tools locally.

Usage:
  python backend/scripts/test_search.py "transformers"

This will run both Semantic Scholar and arXiv search (if available) and print a small
summary. Note: Semantic Scholar has strict rate limits for unauthenticated requests.
"""
import sys
from app.tools import semantic_scholar, arxiv


def run(query):
    print('Query:', query)
    print('\nSemantic Scholar:')
    try:
        ss = semantic_scholar.search_papers(query, limit=5)
        print(f'  Found {len(ss)} results')
        for p in ss[:3]:
            print('  -', p.get('title')[:100])
    except Exception as e:
        print('  Error:', e)

    print('\narXiv:')
    try:
        ax = arxiv.search_papers(query, limit=5)
        print(f'  Found {len(ax)} results')
        for p in ax[:3]:
            print('  -', p.get('title')[:100])
    except Exception as e:
        print('  Error:', e)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python backend/scripts/test_search.py "query"')
        sys.exit(1)
    run(sys.argv[1])
