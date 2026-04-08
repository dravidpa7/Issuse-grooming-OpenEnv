"""
Grader for the medium task.
Partial credit for adjacent priority mistakes. Penalizes loops and wrong closes.
Returns float in [0.0, 1.0].
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from env.tasks.task_medium import MEDIUM_GROUND_TRUTH

PRIORITY_ORDER = ["next_release", "backlog", "wont_fix"]


def grade(trajectory: list, final_state: dict) -> float:
    issues = final_state.get("issues", {})
    ground_truth = MEDIUM_GROUND_TRUTH

    total_items = len(ground_truth)
    triage_correct = 0
    priority_score_sum = 0.0
    priority_total = 0
    duplicate_correct = 0
    duplicate_total = 0
    penalty = 0.0

    # Loop detection from trajectory
    action_counts: dict[str, int] = {}
    for step in trajectory:
        action = step.get("action", {})
        key = f"{action.get('action_type')}:{action.get('payload')}"
        action_counts[key] = action_counts.get(key, 0) + 1
    loop_count = sum(max(0, c - 1) for c in action_counts.values())
    loop_penalty = 0.02 * loop_count

    for item_id_str, issue_data in issues.items():
        item_id = int(item_id_str)
        truth = ground_truth.get(item_id, {})
        if not truth:
            continue

        agent_triage = issue_data.get("triage_state")
        expected_triage = truth.get("triage")

        if agent_triage == expected_triage:
            triage_correct += 1
        elif expected_triage in ("keep", "need-info") and agent_triage == "close":
            penalty += 0.04

        if expected_triage == "duplicate":
            duplicate_total += 1
            if agent_triage == "duplicate" and issue_data.get("duplicate_of") == truth.get("duplicate_of"):
                duplicate_correct += 1

        expected_priority = truth.get("priority")
        if expected_priority:
            priority_total += 1
            agent_priority = issue_data.get("priority")
            if agent_priority == expected_priority:
                priority_score_sum += 1.0
            elif agent_priority in PRIORITY_ORDER and expected_priority in PRIORITY_ORDER:
                dist = abs(PRIORITY_ORDER.index(agent_priority) - PRIORITY_ORDER.index(expected_priority))
                priority_score_sum += max(0.0, 1.0 - 0.5 * dist)

    triage_score   = triage_correct   / total_items
    priority_score = (priority_score_sum / priority_total) if priority_total else 1.0
    dup_score      = (duplicate_correct  / duplicate_total) if duplicate_total else 1.0

    raw = 0.55 * triage_score + 0.35 * priority_score + 0.10 * dup_score
    return max(0.001, min(0.999, raw - penalty - loop_penalty))
