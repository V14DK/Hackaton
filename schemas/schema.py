from pydantic import BaseModel
from typing import Optional
from pydantic import Field


class User(BaseModel):
    username: str
    name: str
    surname: str
    last_name: str
    password: str
    sex: str = Field(max_length=6)
    email: str


class OrgUser(BaseModel):
    id: Optional[int]
    org_id: Optional[int]
    user_id: int


class Organization(BaseModel):
    id: Optional[int]
    name: str


class Event(BaseModel):
    id: Optional[int]
    title: str
    date: str
    count_people: int
    start_time: str
    address: Optional[str]
    icon_id: Optional[str]
    owner: Optional[int]
