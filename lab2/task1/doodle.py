from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
from models import Answer, Poll, Vote

app = FastAPI()
polls = []
votes = []

@app.post("/poll/")
async def post_poll(poll: Poll = Body(...)):
    poll.id = len(polls) + 1  
    polls.append(poll)
    return poll

@app.get("/poll/")
async def get_polls():
    return polls

@app.get("/poll/{id}")
async def get_poll(id: int):
    for poll in polls:
        if poll.id == id:
            return poll
    raise HTTPException(status_code=404, detail="Poll not found")

@app.put("/poll/{id}")
async def put_poll(id: int, poll_update: Poll = Body(...)):
    for index, poll in enumerate(polls):
        if poll.id == id:
            polls[index] = poll_update
            return poll_update
    raise HTTPException(status_code=404, detail="Poll not found")

@app.delete("/poll/{id}")
async def delete_poll(id: int):
    global polls
    polls = [poll for poll in polls if poll.id != id]
    return {"message": "Poll deleted"}

@app.post("/poll/{id}/vote")
async def post_vote(id: int, vote: Vote):
    for poll in polls:
        if poll.id == id:
            for answer in poll.answers:
                if answer.id == vote.answer_id:
                    votes.append({"id": id, "answer_id": vote.answer_id})
                    return {"message": "Vote casted"}
    raise HTTPException(status_code=404, detail="Invalid poll ID or option ID")

@app.get("/poll/{id}/vote")
async def get_vote(id:int):
    return votes


@app.get("/poll/{id}/vote/{id1}")
async def get_vote_id(id1:int):
    for vote in votes:
        if vote["answer_id"] == id:
            return vote
    raise HTTPException(status_code=404, detail="Vote not found")

@app.put("/poll/{id}/vote/{id1}") #put zamienia obecny obiekt na inny
async def put_vote_id(id1:int):
    pass