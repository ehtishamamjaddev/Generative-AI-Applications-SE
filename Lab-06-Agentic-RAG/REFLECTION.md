# Reflection: Lab 06

## What worked well
- The ReAct (Reasoning and Acting) prompt structure effectively guided the LLM (Groq) to use tools accurately.
- FastAPI made exposing the agent logic to a web frontend seamless.

## Challenges faced
- LLM occasionally hallucinated tool names or sent improperly formatted JSON arguments to tools.
- Managing the prompt context window as tool observations grew large.

## How would you fix it
- Enforced strict system prompts dictating exactly how tool JSON responses should be formatted.
- Truncated extreme tool outputs (like massive web page scrapes) before feeding them back into the agent context.

## Production considerations
- Tool access must be sandboxed (e.g., executing calculations in a safe environment to prevent arbitrary code execution).
- Robust LLM retry logic is required: if a tool call fails, the agent should receive the error and try another approach.
- Authentication (OAuth2) and RBAC are necessary to secure the FastAPI endpoints.

## Key learnings
- Creating autonomous LLM agents that interact with external APIs.
- Designing tool docstrings to optimize the LLM's tool-selection accuracy.
