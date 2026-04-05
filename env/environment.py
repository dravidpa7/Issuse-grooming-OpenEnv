import copy
from typing import Optional
from .models import Observation, Action, Reward, Issue
from .tasks.task_easy import EASY_ISSUES, EASY_GROUND_TRUTH
from .tasks.task_medium import MEDIUM_ISSUES, MEDIUM_GROUND_TRUTH
from .tasks.task_hard import HARD_ISSUES, HARD_GROUND_TRUTH
from .graders import grader_easy, grader_medium, grader_hard

TASK_MAP = {
    "easy":   (EASY_ISSUES,   EASY_GROUND_TRUTH,   grader_easy),
    "medium": (MEDIUM_ISSUES, MEDIUM_GROUND_TRUTH, grader_medium),
    "hard":   (HARD_ISSUES,   HARD_GROUND_TRUTH,   grader_hard),
}

VALID_TRIAGE   = {"keep", "close", "need-info", "duplicate"}
VALID_PRIORITY = {"next_release", "backlog", "wont_fix"}
VALID_ACTIONS  = ["triage_item", "mark_duplicate", "set_priority", "done"]

MAX_STEPS = {"easy": 60, "medium": 150, "hard": 300}


class IssueGroomingEnv:
    """
    OpenEnv environment simulating open-source issue grooming.
    The agent reads a backlog of GitHub-style issues/PRs and must:
      - triage_item: assign keep / close / need-info / duplicate
      - mark_duplicate: link a duplicate to its original
      - set_priority: assign next_release / backlog / wont_fix
    Reward is incremental per correct action. Penalties for bad decisions.
    """

    def __init__(self, task_id: str = "easy"):
        if task_id not in TASK_MAP:
            raise ValueError(f"task_id must be one of {list(TASK_MAP)}")
        self.task_id = task_id
        self._issues_template, self._ground_truth, self._grader = TASK_MAP[task_id]
        self._issues: dict[int, Issue] = {}
        self._trajectory: list[dict] = []
        self._step_number: int = 0
        self._done: bool = False
        self._loop_tracker: dict[str, int] = {}

    # ------------------------------------------------------------------ #
    #  OpenEnv interface                                                   #
    # ------------------------------------------------------------------ #

    def reset(self) -> Observation:
        self._issues = {i.id: i.model_copy(deep=True) for i in self._issues_template}
        self._trajectory = []
        self._step_number = 0
        self._done = False
        self._loop_tracker = {}
        return self._make_observation()

    def step(self, action: Action) -> tuple[Observation, Reward, bool, dict]:
        if self._done:
            raise RuntimeError("Episode is done. Call reset() before stepping again.")

        self._step_number += 1
        reward, info = self._apply_action(action)
        self._trajectory.append({"step": self._step_number, "action": action.model_dump(), "reward": reward.value})

        # Terminal conditions
        all_triaged = all(i.triage_state is not None for i in self._issues.values())
        max_steps_reached = self._step_number >= MAX_STEPS[self.task_id]
        done_action = action.action_type == "done"

        self._done = done_action or max_steps_reached

        obs = self._make_observation()
        return obs, reward, self._done, info

    def state(self) -> dict:
        return {
            "task_id": self.task_id,
            "step_number": self._step_number,
            "done": self._done,
            "issues": {iid: i.model_dump() for iid, i in self._issues.items()},
            "trajectory_length": len(self._trajectory),
        }

    # ------------------------------------------------------------------ #
    #  Grading                                                             #
    # ------------------------------------------------------------------ #

    def grade(self) -> float:
        final_state = {
            "issues": {iid: i.model_dump() for iid, i in self._issues.items()}
        }
        return self._grader.grade(self._trajectory, final_state)

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _make_observation(self) -> Observation:
        untriaged = sum(1 for i in self._issues.values() if i.triage_state is None)
        return Observation(
            task_id=self.task_id,
            issues=[i for i in self._issues.values()],
            step_number=self._step_number,
            available_actions=VALID_ACTIONS,
            items_remaining=untriaged,
        )

    def _apply_action(self, action: Action) -> tuple[Reward, dict]:
        atype = action.action_type
        payload = action.payload

        # Loop detection
        loop_key = f"{atype}:{payload}"
        self._loop_tracker[loop_key] = self._loop_tracker.get(loop_key, 0) + 1
        loop_penalty = -0.05 * max(0, self._loop_tracker[loop_key] - 1)

        info = {}

        if atype == "done":
            final_score = self.grade()
            reward_val = max(-1.0, min(1.0, (final_score - 0.5) * 0.4 + loop_penalty))
            return Reward(
                value=round(reward_val, 4),
                breakdown={"final_grade": final_score, "loop_penalty": loop_penalty},
                message=f"Episode ended. Final grade: {final_score:.3f}",
            ), {"final_grade": final_score}

        if atype == "triage_item":
            item_id = payload.get("item_id")
            decision = payload.get("decision")
            comment = payload.get("comment", "")

            if item_id not in self._issues:
                return self._error_reward(f"Unknown item_id {item_id}", loop_penalty), info
            if decision not in VALID_TRIAGE:
                return self._error_reward(f"Invalid decision '{decision}'", loop_penalty), info

            issue = self._issues[item_id]
            issue.triage_state = decision
            issue.comment = comment

            incremental = self._score_triage(item_id, decision)
            reward_val = max(-1.0, min(1.0, incremental + loop_penalty))
            return Reward(
                value=round(reward_val, 4),
                breakdown={"triage_accuracy": incremental, "loop_penalty": loop_penalty},
                message=f"Triaged #{item_id} as '{decision}'. Score: {incremental:+.2f}",
            ), info

        elif atype == "mark_duplicate":
            item_id = payload.get("item_id")
            dup_of = payload.get("duplicate_of")

            if item_id not in self._issues or dup_of not in self._issues:
                return self._error_reward("Invalid item_id or duplicate_of", loop_penalty), info

            issue = self._issues[item_id]
            issue.triage_state = "duplicate"
            issue.duplicate_of = dup_of

            incremental = self._score_duplicate(item_id, dup_of)
            reward_val = max(-1.0, min(1.0, incremental + loop_penalty))
            return Reward(
                value=round(reward_val, 4),
                breakdown={"duplicate_accuracy": incremental, "loop_penalty": loop_penalty},
                message=f"Marked #{item_id} as duplicate of #{dup_of}. Score: {incremental:+.2f}",
            ), info

        elif atype == "set_priority":
            item_id = payload.get("item_id")
            priority = payload.get("priority")

            if item_id not in self._issues:
                return self._error_reward(f"Unknown item_id {item_id}", loop_penalty), info
            if priority not in VALID_PRIORITY:
                return self._error_reward(f"Invalid priority '{priority}'", loop_penalty), info

            issue = self._issues[item_id]
            if issue.triage_state not in ("keep", None):
                # Penalize prioritizing closed/duplicate items
                reward_val = max(-1.0, -0.05 + loop_penalty)
                return Reward(
                    value=round(reward_val, 4),
                    breakdown={"priority_error": -0.05, "loop_penalty": loop_penalty},
                    message=f"Cannot prioritize #{item_id}: triage state is '{issue.triage_state}'",
                ), info

            issue.priority = priority
            incremental = self._score_priority(item_id, priority)
            reward_val = max(-1.0, min(1.0, incremental + loop_penalty))
            return Reward(
                value=round(reward_val, 4),
                breakdown={"priority_accuracy": incremental, "loop_penalty": loop_penalty},
                message=f"Set #{item_id} priority to '{priority}'. Score: {incremental:+.2f}",
            ), info

        else:
            return self._error_reward(f"Unknown action type '{atype}'", loop_penalty), info

    def _score_triage(self, item_id: int, decision: str) -> float:
        truth = self._ground_truth.get(item_id, {})
        expected = truth.get("triage")
        if decision == expected:
            return 0.1
        # Penalize wrong closes of valid issues
        if expected in ("keep", "need-info") and decision == "close":
            return -0.15
        if expected != "duplicate" and decision == "duplicate":
            return -0.08
        return -0.03

    def _score_duplicate(self, item_id: int, dup_of: int) -> float:
        truth = self._ground_truth.get(item_id, {})
        if truth.get("triage") != "duplicate":
            return -0.10  # not a duplicate
        if truth.get("duplicate_of") == dup_of:
            return 0.12
        return -0.05  # right category, wrong target

    def _score_priority(self, item_id: int, priority: str) -> float:
        truth = self._ground_truth.get(item_id, {})
        expected = truth.get("priority")
        if expected is None:
            return -0.05  # should not be prioritized
        if priority == expected:
            return 0.08
        # Adjacent priority: partial credit
        priority_order = ["next_release", "backlog", "wont_fix"]
        try:
            dist = abs(priority_order.index(priority) - priority_order.index(expected))
            return 0.02 if dist == 1 else -0.04
        except ValueError:
            return -0.04

    def _error_reward(self, msg: str, loop_penalty: float) -> Reward:
        val = max(-1.0, -0.02 + loop_penalty)
        return Reward(
            value=round(val, 4),
            breakdown={"error": -0.02, "loop_penalty": loop_penalty},
            message=f"Error: {msg}",
        )
