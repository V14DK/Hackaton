from pydantic import Field
from pydantic import BaseModel
from typing import Optional, List


class FrontTag(BaseModel):
    id: int
    name: str


class CreateUser(BaseModel):
    username: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    last_name: Optional[str]
    password: str
    sex: Optional[str] = Field(max_length=6)
    email: str


class User(BaseModel):
    id: int
    username: Optional[str]
    name: Optional[str]
    surname: Optional[str]
    last_name: Optional[str]
    password: str
    sex: Optional[str] = Field(max_length=6)
    email: str
    icon_id: Optional[str]


class UpdateUser(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    last_name: Optional[str]
    sex: Optional[str]
    icon_id: Optional[str]


class LoginUser(BaseModel):
    email: str
    password: str


class OrgUser(BaseModel):
    id: Optional[int]
    org_id: Optional[int]
    user_id: int


class Organization(BaseModel):
    id: Optional[int]
    name: str


class CreateEvent(BaseModel):
    name: str
    starts_at: Optional[str]
    ends_at: Optional[str]
    description_short: str
    description_html: Optional[str]
    url: Optional[str]
    image_url: Optional[str]
    location: Optional[str]
    geolocation: Optional[List[float]]
    age_limit: Optional[int]
    categories: Optional[List[object]]
    user_id: int


class PriorityEvent(BaseModel):
    event_id: int


class UpdateEvent(BaseModel):
    event_id: int
    name: str
    starts_at: Optional[str]
    ends_at: Optional[str]
    description_short: str
    description_html: Optional[str]
    url: Optional[str]
    image_url: Optional[str]
    location: Optional[str]
    geolocation: Optional[List[float]]
    age_limit: Optional[int]
    categories: Optional[List[object]]


class DeleteEvent(BaseModel):
    id: int


class Event(BaseModel):
    id: int
    name: str
    created_at: str
    starts_at: Optional[str]
    ends_at: Optional[str]
    description_short: str
    description_html: Optional[str]
    url: Optional[str]
    image_url: Optional[str]
    location: Optional[str]
    geolocation: Optional[List[float]]
    age_limit: Optional[int]
    moderation_status: Optional[str]
    access_status: Optional[str]
    categories: Optional[List[object]]
    user_id: int
    priority: bool
    liked: Optional[bool]
    favourited: Optional[bool]
    subscribed: Optional[bool]


class FindEvent(BaseModel):
    name: Optional[str]
    created_at: Optional[List[str]]
    starts_at: Optional[List[str]]
    ends_at: Optional[List[str]]
    age_limit: Optional[int]
    org_id: Optional[int]
    user_id: Optional[int]
    categories: Optional[List[int]]
    priority: Optional[bool]
    sort: Optional[str]


class Set(BaseModel):
    id: int
    name: str
    event_count: int


class JoinEvent(BaseModel):
    id: int


class UserEventTime(BaseModel):
    future_event: List[Event]
    past_event: List[Event]


class AllUserEvent(BaseModel):
    owner: UserEventTime
    member: UserEventTime


class UserWithEvents(BaseModel):
    id: int
    username: str
    name: str
    surname: str
    last_name: str
    sex: str
    email: str
    icon_id: Optional[str]
    events: AllUserEvent


class FrontComment(BaseModel):
    event_id: int
    comment: str
