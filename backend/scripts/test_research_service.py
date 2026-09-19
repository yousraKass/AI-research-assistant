import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services import research as research_service


def main():
    os.environ['LLM_MODEL'] = 'mock'
    q = 'transformer memory efficiency'
    res = research_service.research(q, limit=3)
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
