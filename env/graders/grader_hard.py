"""
Grader for the hard task.
Extra weight on security issues. Cascading duplicate penalty.
Returns float in [0.0, 1.0].
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from env.tasks.task_hard import HARD_GROUND_TRUTH

PRIORITY_ORDER = ["next_release", "backlog", "wont_fix"]
SECURITY_IDS   = {1, 2, 33, 61}   # items where wrong triage carries extra penalty


def grade(trajectory: list, final_state: dict) -> float:
    issues = final_state.get("issues", {})
    ground_truth = HARD_GROUND_TRUTH

    total_items = len(ground_truth)
    triage_correct = 0
    priority_score_sum = 0.0
    priority_total = 0
    duplicate_correct = 0
    duplicate_total = 0
    penalty = 0.0

    # Loop penalty
    action_counts: dict[str, int] = {}
    for step in trajectory:
        action = step.get("action", {})
        key = f"{action.get('action_type')}:{action.get('payload')}"
        action_counts[key] = action_counts.get(key, 0) + 1
    loop_count = sum(max(0, c - 1) for c in action_counts.values())
    loop_penalty = 0.015 * loop_count

    for item_id_str, issue_data in issues.items():
        item_id = int(item_id_str)
        truth = ground_truth.get(item_id, {})
        if not truth:
            continue

        agent_triage = issue_data.get("triage_state")
        expected_triage = truth.get("triage")

        if agent_triage == expected_triage:
            triage_correct += 1
        else:
            if expected_triage in ("keep", "need-info") and agent_triage == "close":
                base_pen = 0.06 if item_id in SECURITY_IDS else 0.03
                penalty += base_pen

        if expected_triage == "duplicate":
            duplicate_total += 1
            if agent_triage == "duplicate":
                expected_dup_of = truth.get("duplicate_of")
                agent_dup_of = issue_data.get("duplicate_of")
                if agent_dup_of == expected_dup_of:
                    duplicate_correct += 1
                else:
                    penalty += 0.02  # linked to wrong canonical

        expected_priority = truth.get("priority")
        if expected_priority:
            priority_total += 1
            agent_priority = issue_data.get("priority")
            if agent_priority == expected_priority:
                priority_score_sum += 1.0
            elif agent_priority in PRIORITY_ORDER and expected_priority in PRIORITY_ORDER:
                dist = abs(PRIORITY_ORDER.index(agent_priority) - PRIORITY_ORDER.index(expected_priority))
                priority_score_sum += max(0.0, 1.0 - 0.5 * dist)
            # Security items: penalize deprioritising
            if item_id in SECURITY_IDS and agent_priority != "next_release" and expected_priority == "next_release":
                penalty += 0.05

    triage_score   = triage_correct   / total_items
    priority_score = (priority_score_sum / priority_total) if priority_total else 1.0
    dup_score      = (duplicate_correct  / duplicate_total) if duplicate_total else 1.0

    raw = 0.55 * triage_score + 0.35 * priority_score + 0.10 * dup_score
    return max(0.0, min(1.0, raw - penalty - loop_penalty))
