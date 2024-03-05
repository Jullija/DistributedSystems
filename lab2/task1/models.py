from typing import List, Optional
from pydantic import BaseModel

class Answer(BaseModel):
    id: int
    description: str

class Poll(BaseModel):
    id: int
    question: str
    answers: List[Answer]

class Vote(BaseModel):
    answer_id: int
