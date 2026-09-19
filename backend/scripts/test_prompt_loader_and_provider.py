import os
import sys

# ensure package imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.llm import provider


def main():
    os.environ['LLM_MODEL'] = 'mock'

    sample_text = (
        "We propose a novel transformer-based architecture that reduces memory "
        "consumption by 2x using a sparse attention mechanism. Experiments on "
        "ImageNet and COCO show competitive accuracy while reducing GPU cost. "
        "This enables training larger models on commodity hardware."
    )

    # Use prompt name (loader will substitute {text})
    out = provider.summarize(sample_text, 'paper_summarization')
    print('\n=== SUMMARY ===\n')
    print(out)


if __name__ == '__main__':
    main()
