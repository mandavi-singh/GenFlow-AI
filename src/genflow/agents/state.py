import operator
from typing import Annotated, Literal

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field


class ResearchState(BaseModel):
    messages: Annotated[list[BaseMessage], operator.add] = Field(default_factory=list)
    query: str = ""
    report: str = ""
    critique: str = ""
    revision_count: int = 0
    status: Literal["working", "done"] = "working"
