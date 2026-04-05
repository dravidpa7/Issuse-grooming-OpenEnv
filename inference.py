"""
Baseline inference script for the Issue Grooming OpenEnv environment.
Uses an OpenAI-compatible API to run an LLM agent over all three tasks.

Environment variables:
    API_BASE_URL  - LLM API endpoint       (default: https://openrouter.ai/api/v1)
    MODEL_NAME    - Model identifier        (default: qwen/qwen3.6-plus:free)
    HF_TOKEN      - API token              (REQUIRED)

Usage (PowerShell):
    $env:HF_TOKEN="sk-or-v1-..."
    $env:API_BASE_URL="https://openrouter.ai/api/v1"
    $env:MODEL_NAME="qwen/qwen3.6-plus:free"
    python inference.py
"""
import os
import sys
import json
import time

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "qwen/qwen3.6-plus:free")
HF_TOKEN     = os.getenv("HF_TOKEN")

# inference.py — change this:
MAX_STEPS = 200   # max steps per task before force-stop

# to match env's actual limits per task:
MAX_STEPS_PER_TASK = {"easy": 60, "medium": 150, "hard": 300}
MAX_FAILS  = 3    # max consecutive parse failures before force-stop
MAX_RETRY  = 5    # max retries on 429 rate limit
RETRY_WAIT = 10   # seconds to wait between retries on 429

if HF_TOKEN is None:
    raise ValueError(
        "HF_TOKEN environment variable is required.\n"
        "Run: $env:HF_TOKEN='sk-or-v1-...'"
    )

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI, RateLimitError
from env import IssueGroomingEnv, Action

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are an experienced open-source maintainer performing issue grooming.
Your job is to triage GitHub issues and PRs efficiently and consistently.

For each step you MUST respond with a single JSON action object. No other text.

Available actions:
1. Triage an item:
   {"action_type": "triage_item", "payload": {"item_id": <int>, "decision": "<keep|close|need-info|duplicate>", "comment": "<optional string>"}}

2. Mark a duplicate:
   {"action_type": "mark_duplicate", "payload": {"item_id": <int>, "duplicate_of": <int>}}

3. Set priority (only for "keep" items):
   {"action_type": "set_priority", "payload": {"item_id": <int>, "priority": "<next_release|backlog|wont_fix>"}}

4. Finish the session:
   {"action_type": "done", "payload": {}}

Triage guidelines:
- keep:      Valid, actionable issue or PR
- close:     Spam, Python 2 requests, add GUI, irreproducible with no info after 1y
- need-info: Bug report missing reproduction steps, version, or OS
- duplicate: Exact same problem as an existing issue (reference the lower-numbered one)

Priority guidelines (for keep items only):
- next_release: Bugs, security issues, broken docs, active PRs
- backlog:      Enhancements, nice-to-haves, long-horizon features
- wont_fix:     Out-of-scope, superseded, or deliberately not doing
"""


# ---------------------------------------------------------------------------
# Observation formatter
# ---------------------------------------------------------------------------
def format_observation(obs) -> str:
    untriaged      = [i for i in obs.issues if i.triage_state is None]
    needs_priority = [
        i for i in obs.issues
        if i.triage_state == "keep" and i.priority is None
    ]

    lines = [
        f"TASK: {obs.task_id} | Step: {obs.step_number} | "
        f"Untriaged: {len(untriaged)} | Needs priority: {len(needs_priority)}\n"
    ]

    if untriaged:
        issue = untriaged[0]
        kind  = "PR" if issue.is_pr else "ISSUE"
        lines.append("NEXT ITEM TO TRIAGE:")
        lines.append(
            f"\n[{kind} #{issue.id}] {issue.title}\n"
            f"  Labels: {issue.labels} | Author: {issue.author_type} | "
            f"Age: {issue.age_days}d | Linked PRs: {issue.linked_prs}\n"
            f"  Body: {issue.body[:300]}{'...' if len(issue.body) > 300 else ''}"
        )
        kept        = [i.id for i in obs.issues if i.triage_state == "keep"]
        triaged_ids = [i.id for i in obs.issues if i.triage_state is not None]
        if triaged_ids:
            lines.append(f"\nAlready triaged IDs: {triaged_ids}")
            lines.append(f"Kept IDs (valid for duplicate_of reference): {kept}")
        lines.append(f"\nRespond with ONE JSON action to triage #{issue.id}.")

    elif needs_priority:
        issue = needs_priority[0]
        lines.append("ALL ITEMS TRIAGED. Now set priorities for kept items.")
        lines.append(
            f"\n[ISSUE #{issue.id}] {issue.title} -- needs priority.\n"
            f"  Respond with: set_priority for item #{issue.id}"
        )

    else:
        lines.append(
            "ALL ITEMS TRIAGED AND PRIORITIZED. Respond with the done action."
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Action parser -- robust against fences, extra text, partial JSON
# ---------------------------------------------------------------------------
def parse_action(text: str) -> Action:
    text = text.strip()

    # Strip markdown code fences
    if "```" in text:
        for part in text.split("```"):
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                text = part
                break

    # Try each line that looks like JSON
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                return Action(**json.loads(line))
            except Exception:
                continue

    # Brace-match to extract first complete {...} block
    start = text.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return Action(**json.loads(text[start:i + 1]))

    raise ValueError(f"No valid JSON found in: {text[:200]!r}")


# ---------------------------------------------------------------------------
# API call with retry on 429 and empty response guard
# ---------------------------------------------------------------------------
def call_api(history: list) -> str:
    for attempt in range(1, MAX_RETRY + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
                temperature=0.0,
                max_tokens=256,
            )

            # Guard: empty choices list
            if not response.choices:
                raise ValueError("API returned empty choices list")

            content = response.choices[0].message.content

            # Guard: None or blank content
            if not content or not content.strip():
                raise ValueError("API returned empty message content")

            return content

        except RateLimitError:
            if attempt == MAX_RETRY:
                raise
            wait = RETRY_WAIT * attempt
            print(
                f"  [429 rate limit] attempt {attempt}/{MAX_RETRY} -- "
                f"waiting {wait}s before retry..."
            )
            time.sleep(wait)

        except ValueError as e:
            if attempt == MAX_RETRY:
                raise
            print(f"  [empty response] attempt {attempt}/{MAX_RETRY} -- retrying in 3s... ({e})")
            time.sleep(3)


# ---------------------------------------------------------------------------
# Per-task runner
# ---------------------------------------------------------------------------
def run_task(task_id: str) -> float:
    env          = IssueGroomingEnv(task_id=task_id)
    obs          = env.reset()
    done         = False
    total_reward = 0.0
    history      = []
    rewards_log  = []
    fail_count   = 0

    print(f"\n[START] task={task_id} env=issue-grooming-env model={MODEL_NAME}")

    try:
        while not done:
            if obs.step_number >= MAX_STEPS_PER_TASK.get(task_id, 300):
                print(f"  [FORCE STOP] step limit {MAX_STEPS} reached")
                break

            obs_text = format_observation(obs)
            history.append({"role": "user", "content": obs_text})

            raw = call_api(history)
            history.append({"role": "assistant", "content": raw})

            try:
                action     = parse_action(raw)
                fail_count = 0
            except Exception as parse_err:
                fail_count += 1
                print(f"  [parse error #{fail_count}] {parse_err}")
                if fail_count >= MAX_FAILS:
                    print(f"  [FORCE STOP] {MAX_FAILS} consecutive parse failures")
                    action = Action(action_type="done", payload={})
                    obs, reward, done, _ = env.step(action)
                    rewards_log.append(reward.value)
                    break
                history.pop()  # discard bad assistant turn, retry same observation
                continue

            obs, reward, done, _ = env.step(action)
            total_reward        += reward.value
            rewards_log.append(reward.value)

            action_str = (
                f"{action.action_type}"
                f"({json.dumps(action.payload, separators=(',', ':'))})"
            )
            print(
                f"  [STEP] step={obs.step_number:3d} | {action_str:55s} | "
                f"reward={reward.value:+.3f} | {reward.message[:55]}"
            )

        final_grade = env.grade()
        success     = final_grade >= 0.5
        rewards_str = ",".join(f"{r:.2f}" for r in rewards_log)
        print(
            f"[END] success={str(success).lower()} "
            f"steps={obs.step_number} rewards={rewards_str}"
        )
        print(f"      Final grade : {final_grade:.4f}")
        print(f"      Total reward: {total_reward:.4f}")
        return final_grade

    except Exception as exc:
        rewards_str = ",".join(f"{r:.2f}" for r in rewards_log)
        print(f"[END] success=false steps={len(rewards_log)} rewards={rewards_str}")
        print(f"      Error: {exc}")
        raise


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    results = {}
    for task_id in ["easy", "medium", "hard"]:
        try:
            results[task_id] = run_task(task_id)
        except Exception as e:
            print(f"  Task '{task_id}' crashed: {e}")
            results[task_id] = 0.0

    print(f"\n{'=' * 60}")
    print("BASELINE RESULTS")
    print("=" * 60)
    for task_id, score in results.items():
        bar = "█" * int(score * 20)
        print(f"  {task_id:8s}: {score:.4f}  {bar}")
    avg = sum(results.values()) / len(results)
    print(f"  {'AVERAGE':8s}: {avg:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()