"""FastAPI reflection agent for iterative Python code generation and review."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from groq import Groq
from pydantic import BaseModel


# Load environment variables before reading the Groq API key.
load_dotenv()


# Application configuration.
MODEL = "llama-3.1-8b-instant"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = FastAPI(title="Reflection Agent", version="1.0")


# Generator prompt: produces the initial Python function.
GENERATOR_PROMPT = (
    "You are an expert Python developer.\n"
    "When given a task, write a clean, working Python function.\n"
    "Include a docstring. Handle edge cases.\n"
    "Return ONLY the Python code — no explanation, no markdown fences."
)


# Critic prompt: evaluates the generated code and returns either issues or APPROVED.
CRITIC_PROMPT = (
    "You are a senior Python code reviewer.\n"
    "Evaluate the given code against these five criteria:\n"
    "1. Correctness   — does it produce the right output?\n"
    "2. Edge cases    — does it handle None, empty, zero, negatives?\n"
    "3. Readability   — clear names, comments, easy to follow?\n"
    "4. Efficiency    — no unnecessary loops or operations?\n"
    "5. Security      — no eval on user input, no hardcoded secrets?\n\n"
    "For each criterion found to have a problem, write:\n"
    "ISSUE [criterion]: <specific problem and why it matters>\n\n"
    "If ALL five criteria are met with no issues, respond with exactly one word:\n"
    "APPROVED\n\n"
    "Never say APPROVED if any criterion has an issue.\n"
    "Be specific. Generic feedback is useless."
)


# Revision prompt: turns critique into the next improved code version.
REVISION_PROMPT = (
    "You are an expert Python developer revising your previous code.\n\n"
    "Your original code:\n"
    "{original}\n\n"
    "Code review critique received:\n"
    "{critique}\n\n"
    "Rewrite the function to fix every issue raised.\n"
    "Do not just acknowledge the critique — actually fix each problem.\n"
    "Return ONLY the corrected Python code."
)


class ReflectRequest(BaseModel):
    """Request body for the /reflect endpoint."""

    task: str
    max_rounds: int = 3


class ReflectResponse(BaseModel):
    """Response body returned by the reflection workflow."""

    final_code: str
    round_count: int
    approved: bool
    critiques: list[str]


def call_llm(system: str, user: str) -> str:
    """Call the Groq chat completion API and return the trimmed assistant reply."""

    if client is None:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured in the environment.",
        )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive API error handling.
        raise HTTPException(
            status_code=502,
            detail=f"Groq API request failed: {exc}",
        ) from exc

    message = response.choices[0].message.content if response.choices else None
    if message is None:
        raise HTTPException(
            status_code=502,
            detail="Groq API returned an empty response.",
        )

    return message.strip()


def run_reflection(task: str, max_rounds: int) -> ReflectResponse:
    """Generate code, critique it, and iteratively revise until approved or exhausted."""

    # Round 0: create the initial implementation from the task description.
    current_code = call_llm(
        GENERATOR_PROMPT,
        f"Write a Python function for this task:\n{task}",
    )

    critiques: list[str] = []

    # Reflection rounds: critique the latest code, then revise if needed.
    for round_number in range(1, max_rounds + 1):
        critique = call_llm(
            CRITIC_PROMPT,
            f"Review this Python code:\n\n{current_code}",
        )

        if critique.strip().upper() == "APPROVED":
            critiques.append("APPROVED")
            return ReflectResponse(
                final_code=current_code,
                round_count=round_number,
                approved=True,
                critiques=critiques,
            )

        critiques.append(critique)

        revision_prompt = REVISION_PROMPT.format(
            original=current_code,
            critique=critique,
        )
        current_code = call_llm(GENERATOR_PROMPT, revision_prompt)

    # Safety stop: return the best code reached when the maximum rounds are used up.
    return ReflectResponse(
        final_code=current_code,
        round_count=max_rounds,
        approved=False,
        critiques=critiques,
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple health status and the active model name."""

    return {"status": "ok", "model": MODEL}


@app.post("/reflect", response_model=ReflectResponse)
def reflect_endpoint(req: ReflectRequest) -> ReflectResponse:
    """Run the reflection workflow for the requested programming task."""

    if not req.task.strip():
        raise HTTPException(status_code=400, detail="task must not be empty")

    if req.max_rounds < 1:
        raise HTTPException(status_code=400, detail="max_rounds must be at least 1")

    return run_reflection(req.task.strip(), req.max_rounds)