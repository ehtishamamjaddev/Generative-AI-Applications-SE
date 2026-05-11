# Reflection: Lab 02

## What worked well
- Google Sheets API integration provided an intuitive database for inputs and outputs.
- Prompting the LLM with specific generation constraints worked most of the time.

## Challenges faced
- Hitting API quota limits with the initial LLM provider (Gemini).
- Extracting and counting words via workflow expressions for the Quality Gate.

## How would you fix it
- Pivoted to Groq (llama3-8b), which provided faster inference and accommodated the requested rate limits.
- Implemented regex/split expressions to accurately parse the word count.

## Production considerations
- API rate limits must be gracefully handled via retry logic or exponential backoff nodes.
- Prompts should be parameterized and stored as environment variables.

## Key learnings
- Prompt engineering for workflow automation.
- Evaluating and validating LLM outputs programmatically.
