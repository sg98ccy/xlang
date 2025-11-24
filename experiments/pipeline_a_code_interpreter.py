# ============================================================
# Pipeline A (Baseline)
# LLM + Code Interpreter (Python sandbox) → Excel
# ============================================================

import os
import json
from pathlib import Path

from openai import OpenAI

# Optional: load .env in local dev (do NOT commit .env)
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()
except ImportError:
    # Safe to ignore if you do not want dotenv
    pass


# ============================================================
# 1. Configuration and paths
# ============================================================

MODEL_NAME = "gpt-4.1"  # adjust as required

# This script is expected to live in: <repo_root>/experiments/pipeline_a_code_interpreter.py
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

PROMPT_DIR = SCRIPT_DIR / "prompts" / "pipeline_a"
RESULTS_DIR = SCRIPT_DIR / "results" / "pipelineA_codeInterpreter"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_prompt(filename: str) -> str:
    """
    Load a prompt text file from the pipeline_a prompt directory.
    """
    path = PROMPT_DIR / filename
    return path.read_text(encoding="utf-8")


# ============================================================
# 2. Client initialisation and API key handling
# ============================================================

def create_client() -> OpenAI:
    """
    Create an OpenAI client using the OPENAI_API_KEY environment variable.

    Security best practice:
    - Set OPENAI_API_KEY in your environment (or .env for local dev).
    - Never hardcode the key in source code.
    - Ensure .env is in .gitignore.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment.")
    return OpenAI(api_key=api_key)


# ============================================================
# 3. Single run of Pipeline A using Responses + Code Interpreter
# ============================================================

def run_pipeline_a_once(run_index: int = 1) -> None:
    client = create_client()

    developer_instructions = load_prompt("developer_instructions.txt")
    user_prompt = load_prompt("user_prompt_sales_dashboard.txt")

    print(f"[Pipeline A] Run {run_index}: calling model {MODEL_NAME} with code_interpreter...")

    response = client.responses.create(
        model=MODEL_NAME,
        tools=[
            {
                "type": "code_interpreter",
                "container": {"type": "auto"},
            }
        ],
        instructions=developer_instructions,
        input=user_prompt,
        store=False,
    )

    # Save full response for inspection (tools, outputs, etc.)
    out_path = RESULTS_DIR / f"pipelineA_run_{run_index:03d}.json"
    with out_path.open("w", encoding="utf-8") as f:
        # model_dump() gives a plain dict that is JSON serialisable
        json.dump(response.model_dump(), f, indent=2)
    print(f"[Pipeline A] Saved raw response to: {out_path}")

    # --------------------------------------------------------
    # Token usage (this is what you care about for comparison)
    # --------------------------------------------------------
    usage = getattr(response, "usage", None)
    if usage is not None:
        # The Responses API exposes usage fields such as:
        #   usage.input_tokens, usage.output_tokens, usage.total_tokens
        input_tokens = getattr(usage, "input_tokens", None)
        output_tokens = getattr(usage, "output_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)

        print(f"[Pipeline A] Token usage:")
        print(f"  input_tokens:  {input_tokens}")
        print(f"  output_tokens: {output_tokens}")
        print(f"  total_tokens:  {total_tokens}")
    else:
        print("[Pipeline A] Warning: no usage information returned by API")

    # Optional: quick text view of what the model said (including tool summary)
    # Many SDK versions provide a convenience method:
    # print("[Pipeline A] Output text:")
    # print(response.output_text)


# ============================================================
# 4. Entry point
# ============================================================

if __name__ == "__main__":
    run_pipeline_a_once(run_index=1)
