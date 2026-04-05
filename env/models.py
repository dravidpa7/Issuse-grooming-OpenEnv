from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class Issue(BaseModel):
    id: int
    title: str
    body: str
    labels: List[str]
    author_type: str  # "maintainer", "contributor", "new_user"
    age_days: int
    linked_prs: List[int]
    is_pr: bool = False
    triage_state: Optional[str] = None  # keep, close, need-info, duplicate
    priority: Optional[str] = None      # next_release, backlog, wont_fix
    comment: Optional[str] = None
    duplicate_of: Optional[int] = None


class Observation(BaseModel):
    task_id: str
    issues: List[Issue]
    step_number: int
    available_actions: List[str]
    items_remaining: int


class Action(BaseModel):
    action_type: str  # triage_item, mark_duplicate, set_priority
    payload: Dict[str, Any]


class Reward(BaseModel):
    value: float
    breakdown: Dict[str, float]
    message: str
