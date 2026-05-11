"""FastAPI reflection agent using Ollama local model instead of Groq cloud API.

This implementation demonstrates the provider-agnostic Reflection Pattern:
- Same generator-critic loop as main.py (Groq version)
- Same prompts, stopping conditions, response schema
- Only call_llm() changes to use Ollama's local HTTP API
- Swappable providers without rewriting core reflection logic
"""

from __future__ import annotations

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Reflection Pattern - Code Review Agent (Ollama)",
    version="1.0"
)

# Local Ollama model endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:0.5b"


class ReflectionRequest(BaseModel):
    """Request body for the /reflect endpoint."""

    task: str
    max_rounds: int = 3


class CritiqueRound(BaseModel):
    """A single round of critique feedback."""

    round: int
    critique: str
    approved: bool


class ReflectionResponse(BaseModel):
    """Response body returned by the reflection workflow."""

    final_code: str
    round_count: int
    approved: bool
    critiques: list[CritiqueRound]


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Call Ollama local model instead of Groq.

    Ollama exposes a local HTTP API at localhost:11434.

    Key differences from Groq implementation:
    - Uses local qwen2.5:0.5b model (no API key needed)
    - HTTP POST to localhost:11434/api/generate
    - Combines system and user prompts into single prompt field
    - Response format: data["response"] instead of data.choices[0].message.content
    """

    payload = {
        "model": MODEL,
        "prompt": f"System: {system_prompt}\n\nUser: {user_prompt}",
        "stream": False,  # Get complete response, not streaming
        "options": {
            "temperature": 0.3  # Same low temperature for consistent code generation
        },
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=(
                "Ollama server not running at http://localhost:11434. "
                "Start it with: ollama serve"
            ),
        ) from e
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama API error: {e}",
        ) from e

    data = response.json()
    return data.get("response", "").strip()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint - verifies Ollama server is running.

    Returns the local model name instead of Groq's cloud model.
    """

    return {
        "status": "ok",
        "model": MODEL,
        "pattern": "Reflection (Generator-Critic loop)",
    }


@app.post("/reflect", response_model=ReflectionResponse)
def reflect(request: ReflectionRequest) -> ReflectionResponse:
    """Run the reflection workflow for the requested programming task.

    IMPORTANT: This is IDENTICAL to the Groq version in main.py.
    The only difference is which LLM provider the call_llm() function uses.

    The loop:
    1. Generator produces code for the task
    2. Critic evaluates against 5-criterion checklist
    3. If APPROVED, exit. If not, feed critique back to Generator
    4. Repeat until approved or max_rounds reached
    """

    if not request.task.strip():
        raise HTTPException(status_code=400, detail="task must not be empty")

    if request.max_rounds < 1:
        raise HTTPException(status_code=400, detail="max_rounds must be at least 1")

    # IDENTICAL prompts to Groq version - demonstrating provider-agnostic design
    GENERATOR_PROMPT = (
        "You are an expert Python developer. "
        "Write clean, efficient, secure Python code. "
        "When given a task, produce only the Python function with proper docstring. "
        "No explanations, no markdown fences."
    )

    CRITIC_PROMPT = (
        "You are a ruthless code reviewer. Evaluate Python code against these criteria:\n"
        "1. Correctness: Does it solve the task completely?\n"
        "2. Edge cases: Does it handle empty inputs, None, invalid types?\n"
        "3. Readability: Clear variable names, docstring present?\n"
        "4. Efficiency: Reasonable time/space complexity?\n"
        "5. Security: No eval(), exec(), or SQL injection risks?\n\n"
        "If ALL criteria pass, respond with exactly: APPROVED - All criteria met.\n"
        "If ANY criterion fails, list the specific issues. Be concise but specific."
    )

    task = request.task.strip()
    max_rounds = request.max_rounds
    critiques: list[CritiqueRound] = []
    current_code = ""
    approved = False

    # IDENTICAL loop logic to Groq version
    for round_num in range(1, max_rounds + 1):
        # Generator step
        if round_num == 1:
            generator_input = f"Write a Python function for this task:\n{task}"
        else:
            generator_input = (
                f"Original task: {task}\n\n"
                f"Previous code:\n{current_code}\n\n"
                f"Critic feedback:\n{critiques[-1].critique}\n\n"
                "Revise the code to address all issues. Return ONLY the corrected code."
            )

        current_code = call_llm(GENERATOR_PROMPT, generator_input)

        # Critic step
        critic_input = f"Task: {task}\n\nCode to review:\n{current_code}"
        critique_text = call_llm(CRITIC_PROMPT, critic_input)

        # Check if approved
        is_approved = "APPROVED" in critique_text.upper()

        critiques.append(
            CritiqueRound(round=round_num, critique=critique_text, approved=is_approved)
        )

        if is_approved:
            approved = True
            break

    return ReflectionResponse(
        final_code=current_code,
        round_count=len(critiques),
        approved=approved,
        critiques=critiques,
    )
