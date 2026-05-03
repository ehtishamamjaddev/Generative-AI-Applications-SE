# Reflection: Lab 04

## What worked well
- The strict fallback mechanism (`no_context`) was highly effective in preventing LLM hallucinations.
- Audit logging provided transparent insight into the model's reasoning.

## Challenges faced
- Keyword-based retrieval struggles with synonyms and semantic meaning (e.g., "money laundering" vs "AML").

## How would you fix it
- Acknowledged the limitation, noting that shifting to vector embeddings (Lab 05) will solve semantic mismatches.

## Production considerations
- Financial platforms require strict compliance; audit logs must be immutable and securely stored.
- PII/sensitive data should be redacted before logging or sending to the external LLM.

## Key learnings
- Grounding LLMs in external truth.
- Threshold engineering to balance recall and precision.
