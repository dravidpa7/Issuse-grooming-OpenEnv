# issue-grooming-env

An [OpenEnv](https://openenv.dev)-compatible RL environment simulating **open-source issue grooming** — the weekend ritual of small repo maintainers who clean up GitHub backlogs.

## Overview & Motivation

Small open-source repos (< 500 stars) accumulate issue debt fast: duplicates, vague reports, stale PRs, and items that will never be fixed. Maintainers spend hours triaging manually. This environment trains an agent to do that work — consistently and efficiently — using the same judgment a seasoned maintainer would apply.

---

## Observation Space

| Field | Type | Description |
|---|---|---|
| `task_id` | `str` | `easy`, `medium`, or `hard` |
| `issues` | `List[Issue]` | Full backlog with id, title, body, labels, author_type, age_days, linked_prs, triage_state, priority |
| `step_number` | `int` | Current step count |
| `available_actions` | `List[str]` | `triage_item`, `mark_duplicate`, `set_priority`, `done` |
| `items_remaining` | `int` | Count of untriaged items |

---

## Action Space

| Action | Payload | Description |
|---|---|---|
| `triage_item` | `{item_id, decision, comment?}` | Assign `keep / close / need-info / duplicate` |
| `mark_duplicate` | `{item_id, duplicate_of}` | Link item to its canonical issue |
| `set_priority` | `{item_id, priority}` | Assign `next_release / backlog / wont_fix` |
| `done` | `{}` | End grooming session |

---

## Tasks

| Task ID | Items | Key Challenges |
|---|---|---|
| `easy` | 10 | Clean backlog, one obvious duplicate pair |
| `medium` | 30 | Noisy descriptions, multiple duplicate clusters, stale items |
| `hard` | 61 | Security issues, cascading duplicates, two-release scope, conflicting signals |

### Grading (all tasks)
- Triage accuracy 55% · Priority accuracy 35% · Duplicate accuracy 10%
- Penalties for wrongly closing valid issues, wrong duplicate targets, loop actions

---

## Environment Variables

| Variable | Default | Required |
|---|---|---|
| `HF_TOKEN` | — | ✅ Yes |
| `API_BASE_URL` | `https://api.openai.com/v1` | No |
| `MODEL_NAME` | `gpt-4.1-mini` | No |

---

## Setup & Usage

```bash
pip install -r requirements.txt

# Run baseline agent
HF_TOKEN=hf_... python inference.py

# Custom endpoint
HF_TOKEN=hf_... API_BASE_URL=http://localhost:8000/v1 MODEL_NAME=Qwen3-VL-30B python inference.py
```

### Docker

```bash
docker build -t issue-grooming-env .
docker run -e HF_TOKEN=$HF_TOKEN issue-grooming-env
```

### Use as a library

```python
from env import IssueGroomingEnv, Action

env = IssueGroomingEnv(task_id="easy")
obs = env.reset()
obs, reward, done, info = env.step(
    Action(action_type="triage_item", payload={"item_id": 1, "decision": "keep"})
)
print(reward.message)
print(env.grade())
```

---

## Baseline Performance

| Task | Score |
|---|---|
| easy | TBD |
| medium | TBD |
| hard | TBD |

---

## Repository Structure

```
issue-grooming-env/
├── env/
│   ├── __init__.py
│   ├── environment.py
│   ├── models.py
│   ├── tasks/
│   │   ├── task_easy.py
│   │   ├── task_medium.py
│   │   └── task_hard.py
│   └── graders/
│       ├── grader_easy.py
│       ├── grader_medium.py
│       └── grader_hard.py
├── inference.py             # Root — required by hackathon
├── openenv.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```
