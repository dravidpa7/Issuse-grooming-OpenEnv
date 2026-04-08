import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
import uvicorn

from env import IssueGroomingEnv, Action

app = FastAPI()
env = IssueGroomingEnv(task_id="easy")

class ResetRequest(BaseModel):
    task_id: Optional[str] = "easy"

class StepRequest(BaseModel):
    action_type: str
    payload: Dict[str, Any] = {}

@app.post("/reset")
def reset(request: Optional[ResetRequest] = None):
    global env
    task_id = request.task_id if request else "easy"
    env = IssueGroomingEnv(task_id=task_id)
    obs = env.reset()
    return JSONResponse(content=obs.model_dump())

@app.post("/step")
def step(request: StepRequest):
    action = Action(action_type=request.action_type, payload=request.payload)
    obs, reward, done, info = env.step(action)
    return JSONResponse(content={
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info
    })

@app.get("/state")
def state():
    return JSONResponse(content=env.state())

@app.get("/")
def health():
    return {"status": "ok"}

def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()