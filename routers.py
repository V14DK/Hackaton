from typing import List
from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from core.models.database import get_session
from fastapi.security import OAuth2PasswordBearer
# from fastapi.security import OAuth2PasswordRequestForm
from core.auth.service import validate_create_user, user_login, get_user_profile, remove_token, update_profile
from core.schemas.schema import User, CreateUser, LoginUser, Event, CreateEvent, UpdateEvent, DeleteEvent, FrontTag, \
    Set, FindEvent, UserWithEvents, AllUserEvent, FrontComment, UpdateUser, PriorityEvent
from core.events.service import add_event, read_events, read_my_events, change_event, delete_event, map_tags, read_sets, \
    like_dislike_event, subscribe_event, read_user, write_comment, set_priority, favourite_event


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
router = APIRouter()


@router.post("/login", tags=['account'])
async def login(form_data: LoginUser, session: Session = Depends(get_session)):
    auth = user_login(form_data, session)
    auth.update({"message": "Successful login"})
    profile = get_user_profile(auth.get('access_token'), session)
    auth.update(**profile.dict())
    return JSONResponse(content=auth)


@router.post("/register", tags=['account'])
async def register(form_data: CreateUser, session: Session = Depends(get_session)) -> object:
    auth = validate_create_user(form_data, session)
    auth.update({"message": "User is created"})
    return JSONResponse(content=auth)


@router.get("/logout", tags=['account'])
async def logout(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return remove_token(token, session)


@router.get("/profile", response_model=User, tags=['account'])
async def get_profile(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return get_user_profile(token, session)


@router.post('/profile/change', tags=['account'])
async def change_profile(update_user: UpdateUser, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return update_profile(user=token, update_user=update_user, session=session)


@router.get('/user', response_model=UserWithEvents, tags=['other user'])
async def get_user_info(user: str, session: Session = Depends(get_session)):
    return read_user(user, session)


@router.post('/events/create', tags=['events'])
async def create_event(event: CreateEvent, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return add_event(user=token, session=session, event=event)


@router.post('/priority', tags=['events'])
async def priority_event(event: PriorityEvent, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return set_priority(user=token, session=session, event=event)


@router.post('/events/update', tags=['events'])
async def update_event(event: UpdateEvent, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return change_event(user=token, session=session, event=event)


@router.post('/events/delete', tags=['events'])
async def remove_event(event: DeleteEvent, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return delete_event(user=token, session=session, event=event)


@router.get('/events', response_model=List[Event], tags=['events'])
async def get_events(session: Session = Depends(get_session), id: int = None):
    return read_events(session=session, id=id)


# @router.get('/events_with_token', response_model=List[Event], tags=['events'])
# async def get_events_with_token(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session), id: int = None):
#     return read_events(user=token, session=session, id=id, auth=True)


@router.get('/events/my', response_model=AllUserEvent, tags=['events'])
async def get_my_events(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return read_my_events(user=token, session=session)


@router.post('/find', response_model=List[Event], tags=['events'])
async def find_events(filter: FindEvent, session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    return read_events(session, **filter.dict())


@router.post('/events', response_model=List[Event], tags=['events'])
async def event_with_token(filter: FindEvent, session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    return read_events(session, user=token, **filter.dict())


@router.get('/tags', response_model=List[FrontTag], tags=['events'])
async def get_tags():
    return [FrontTag(id=value, name=key) for key, value in map_tags.items()]


@router.get('/sets', response_model=List[Set], tags=['events'])
async def get_sets(session: Session = Depends(get_session)):
    return read_sets(session)


@router.post('/like', tags=['events'])
async def like_event(id: PriorityEvent, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return like_dislike_event(user=token, id=id.event_id, session=session)


@router.post('/subscribe', tags=['events'])
async def subscribe(id: PriorityEvent, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return subscribe_event(user=token, id=id.event_id, session=session)


@router.post('/favourite', tags=['events'])
async def favourite(id: PriorityEvent, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return favourite_event(user=token, id=id.event_id, session=session)


@router.post('/comment', tags=['events'])
async def comment(comment: FrontComment, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    return write_comment(user=token, comment=comment, session=session)


app.include_router(router)
