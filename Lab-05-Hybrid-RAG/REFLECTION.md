# Reflection: Lab 05

## What worked well
- Semantic search dramatically improved the user experience by understanding intent rather than just vocabulary.
- The Pinecone integration was fast and easily handled the 768-dimensional embeddings.

## Challenges faced
- Tuning the dynamic threshold; setting it too high resulted in false negatives, too low allowed irrelevant context.
- Managing chunk overlap and embedding generation.

## How would you fix it
- Settled on a baseline threshold of ~0.60 to 0.70 depending on the domain strictness.
- Standardized chunking to 512 tokens with a 50-token overlap to maintain context across boundaries.

## Production considerations
- Vector databases need proper namespace isolation (e.g., separating patient/healthcare data from financial data).
- Embedding models should ideally be hosted locally (like Ollama) if extreme data privacy is required.

## Key learnings
- Vector vs. Keyword retrieval trade-offs.
- Multi-domain knowledge separation strategies.
