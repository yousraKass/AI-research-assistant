"""Test script for the LLM provider summarize() function.

Usage: python backend/scripts/test_llm_provider.py
"""
from app.llm.provider import summarize


SAMPLE_ABSTRACT = (
    """
    We introduce a novel approach to large-scale language understanding that
    combines contrastive learning with sparse attention. Our experiments on
    synthetic and real-world datasets show improved sample efficiency and
    robust generalization across tasks. We also provide a theoretical analysis
    of convergence properties and demonstrate state-of-the-art performance on
    multiple benchmarks.
    """
)

PROMPT_TEMPLATE = (
    "You are an assistant that produces concise academic summaries."
    "Summarize the following abstract in 2-3 sentences, highlighting the"
    "method, key result, and significance."
)


def main():
    print('Running LLM provider summarize test...')
    summary = summarize(SAMPLE_ABSTRACT, PROMPT_TEMPLATE)
    print('\nSUMMARY:\n')
    print(summary)


if __name__ == '__main__':
    main()
