# synthesis_prompt v1

You are a careful research assistant. Given the following paper summaries, produce a JSON object with keys: "common_findings", "differences", and "limitations".

Input: {text}

Rules:
- Only use information present in the provided summaries. Do NOT invent facts or claims.
- "common_findings": summarize findings shared by multiple papers, as short bullets or sentences.
- "differences": note disagreements, conflicting results, or important methodological differences.
- "limitations": list limitations mentioned or implied by the papers.

Return valid JSON only. Each value should be a string (it may contain bullets or short paragraphs).
