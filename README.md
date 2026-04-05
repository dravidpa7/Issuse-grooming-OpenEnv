<div align="center">

<svg width="80" height="80" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="72" height="72" rx="16" fill="#0d2116" stroke="#3fb950" stroke-width="1.5"/>
  <circle cx="14" cy="14" r="1.2" fill="#1a4429"/>
  <circle cx="26" cy="14" r="1.2" fill="#1a4429"/>
  <circle cx="38" cy="14" r="1.2" fill="#1a4429"/>
  <circle cx="50" cy="14" r="1.2" fill="#1a4429"/>
  <circle cx="58" cy="14" r="1.2" fill="#1a4429"/>
  <circle cx="14" cy="58" r="1.2" fill="#1a4429"/>
  <circle cx="26" cy="58" r="1.2" fill="#1a4429"/>
  <circle cx="38" cy="58" r="1.2" fill="#1a4429"/>
  <circle cx="50" cy="58" r="1.2" fill="#1a4429"/>
  <circle cx="58" cy="58" r="1.2" fill="#1a4429"/>
  <rect x="20" y="22" width="6" height="6" rx="3" fill="#3fb950"/>
  <rect x="30" y="24" width="22" height="2" rx="1" fill="#3fb950" opacity="0.9"/>
  <rect x="30" y="28" width="14" height="1.5" rx="0.75" fill="#3fb950" opacity="0.4"/>
  <rect x="20" y="33" width="6" height="6" rx="3" fill="#3fb950" opacity="0.6"/>
  <rect x="30" y="35" width="18" height="2" rx="1" fill="#3fb950" opacity="0.6"/>
  <rect x="30" y="39" width="10" height="1.5" rx="0.75" fill="#3fb950" opacity="0.3"/>
  <rect x="20" y="44" width="6" height="6" rx="3" fill="#3fb950" opacity="0.35"/>
  <rect x="30" y="46" width="20" height="2" rx="1" fill="#3fb950" opacity="0.35"/>
  <rect x="30" y="50" width="12" height="1.5" rx="0.75" fill="#3fb950" opacity="0.2"/>
  <path d="M22 25 L24 27 L27 23" stroke="#0d2116" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>

# issue-grooming-env

**An [OpenEnv](https://openenv.dev)-compatible RL environment simulating open-source issue grooming.**

![OpenEnv](https://img.shields.io/badge/OpenEnv-v1.0.0-3fb950?style=flat-square&labelColor=0d2116)
![Python](https://img.shields.io/badge/Python-3.11+-79c0ff?style=flat-square&labelColor=0d1117)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-f778ba?style=flat-square&labelColor=0d1117)
![Tasks](https://img.shields.io/badge/Tasks-3-e3b341?style=flat-square&labelColor=0d1117)

</div>

---

## Overview & Motivation

Small open-source repos (< 500 stars) accumulate issue debt fast: duplicates, vague reports, stale PRs, and items that will never be fixed. Maintainers spend hours triaging manually. This environment trains an agent to do that work — consistently and efficiently — using the same judgment a seasoned maintainer would apply.

---

## Baseline Performance

| Task | Score | Items | Key Challenge |
|---|---|---|---|
| `easy` | **1.0000** | 10 | Clean backlog, one obvious duplicate pair |
| `medium` | **0.9363** | 30 | Noisy descriptions, multiple duplicate clusters |
| `hard` | **0.9257** | 61 | Security issues, cascading duplicates, two-release scope |

**Grading weights:** Triage accuracy 55% · Priority accuracy 35% · Duplicate accuracy 10%

> Run `python inference.py` and paste your scores above.

---

## Determinism Verification

The grader is a pure function of agent decisions — no randomness, no external calls.

```
easy    : 0.4150 × 5 → ✅ DETERMINISTIC  
medium  : 0.6029 × 5 → ✅ DETERMINISTIC  
hard    : 0.3882 × 5 → ✅ DETERMINISTIC  
```

> Run `python test_determinism.py` and paste results above.

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
| `mark_duplicate` | `{item_id, duplicate_of}` | Link item to its canonical lower-numbered issue |
| `set_priority` | `{item_id, priority}` | Assign `next_release / backlog / wont_fix` — kept items only |
| `done` | `{}` | End grooming session |

---

## Reward Signals

| Decision | Score |
|---|---|
| Correct triage | `+0.10` |
| Correct duplicate + correct target | `+0.12` |
| Correct priority | `+0.08` |
| Priority off by one level | `+0.02` |
| Wrong close of valid / need-info issue | `−0.15` |
| Wrong duplicate on non-duplicate | `−0.08` |
| Correct duplicate, wrong target | `−0.05` |
| Prioritizing closed / duplicate item | `−0.05` |
| Loop penalty (repeated identical action) | `−0.05 × repeat` |

---

## Environment Variables

| Variable | Default | Required |
|---|---|---|
| `HF_TOKEN` | — | ✅ Yes |
| `API_BASE_URL` | `https://openrouter.ai/api/v1` | No |
| `MODEL_NAME` | `qwen/qwen3.6-plus:free` | No |

---

## Setup & Usage

```bash
pip install -r requirements.txt
```

```powershell
# PowerShell
$env:HF_TOKEN="sk-or-v1-..."
python inference.py

# Custom endpoint (Groq recommended for stability)
$env:API_BASE_URL="https://api.groq.com/openai/v1"
$env:MODEL_NAME="llama-3.1-8b-instant"
python inference.py
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
print(reward.message)   # Triaged #1 as 'keep'. Score: +0.10
print(env.grade())      # 0.0–1.0
```

---

## Repository Structure

```
issue-grooming-env/
├── env/
│   ├── __init__.py
│   ├── environment.py        # OpenEnv class · reset / step /state / grade
│   ├── models.py             # Pydantic: Issue, Observation, Action, Reward
│   ├── tasks/
│   │   ├── task_easy.py
│   │   ├── task_medium.py
│   │   └── task_hard.py
│   └── graders/
│       ├── grader_easy.py
│       ├── grader_medium.py
│       └── grader_hard.py
├── inference.py              # Baseline LLM agent · hackathon entry point
├── test_determinism.py       # Proves grader is deterministic
├── openenv.yaml
├── Dockerfile
├── requirements.txt          # openai>=1.0.0, pydantic>=2.0.0
└── README.md
```
