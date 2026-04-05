"""
Proves env.grade() is deterministic — same actions → same score every time.
Run: python test_determinism.py
"""
from env import IssueGroomingEnv, Action

def run_fixed_sequence(task_id: str) -> float:
    env = IssueGroomingEnv(task_id=task_id)
    obs = env.reset()
    
    # Always triage the first untriaged item as "keep" until done
    for _ in range(500):
        untriaged = [i for i in obs.issues if i.triage_state is None]
        needs_priority = [
            i for i in obs.issues
            if i.triage_state == "keep" and i.priority is None
        ]
        
        if untriaged:
            action = Action(
                action_type="triage_item",
                payload={"item_id": untriaged[0].id, "decision": "keep"}
            )
        elif needs_priority:
            action = Action(
                action_type="set_priority",
                payload={"item_id": needs_priority[0].id, "priority": "backlog"}
            )
        else:
            action = Action(action_type="done", payload={})
        
        obs, reward, done, _ = env.step(action)
        if done:
            break
    
    return env.grade()

if __name__ == "__main__":
    for task_id in ["easy", "medium", "hard"]:
        scores = [run_fixed_sequence(task_id) for _ in range(5)]
        all_same = len(set(scores)) == 1
        status = "✅ DETERMINISTIC" if all_same else "❌ VARIES"
        print(f"{task_id:8s}: {scores} → {status}")