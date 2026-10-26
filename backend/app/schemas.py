from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
Status = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]


class TaskCreate(BaseModel):
    title: Title
    description: str | None = None
    status: Status = "todo"
    user_id: int | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: str
    created_at: datetime
    user_id: int | None = None
    due_date: datetime | None = None
