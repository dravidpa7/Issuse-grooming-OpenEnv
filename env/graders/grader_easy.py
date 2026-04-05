"""
Grader for the easy task.
Returns a float in [0.0, 1.0].
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from env.tasks.task_easy import EASY_GROUND_TRUTH


def grade(trajectory: list, final_state: dict) -> float:
    issues = final_state.get("issues", {})
    ground_truth = EASY_GROUND_TRUTH

    total_items = len(ground_truth)
    triage_correct = 0
    priority_correct = 0
    priority_total = 0
    duplicate_correct = 0
    duplicate_total = 0
    penalty = 0.0

    for item_id_str, issue_data in issues.items():
        item_id = int(item_id_str)
        truth = ground_truth.get(item_id, {})
        if not truth:
            continue

        agent_triage = issue_data.get("triage_state")
        expected_triage = truth.get("triage")

        # Triage scoring
        if agent_triage == expected_triage:
            triage_correct += 1
        elif expected_triage in ("keep", "need-info") and agent_triage == "close":
            penalty += 0.05  # wrongly closing valid issues

        # Duplicate scoring
        if expected_triage == "duplicate":
            duplicate_total += 1
            if agent_triage == "duplicate":
                expected_dup_of = truth.get("duplicate_of")
                agent_dup_of = issue_data.get("duplicate_of")
                if agent_dup_of == expected_dup_of:
                    duplicate_correct += 1

        # Priority scoring (only for kept items)
        expected_priority = truth.get("priority")
        if expected_priority:
            priority_total += 1
            agent_priority = issue_data.get("priority")
            if agent_priority == expected_priority:
                priority_correct += 1

    # Weights: triage 55%, priority 35%, duplicate 10%
    triage_score   = triage_correct   / total_items
    priority_score = (priority_correct / priority_total) if priority_total else 1.0
    dup_score      = (duplicate_correct / duplicate_total) if duplicate_total else 1.0

    raw = 0.55 * triage_score + 0.35 * priority_score + 0.10 * dup_score
    return max(0.0, min(1.0, raw - penalty))
