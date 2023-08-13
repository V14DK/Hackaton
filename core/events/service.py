import json
import datetime
from fastapi import HTTPException
from core.auth import check_token
from sqlalchemy.orm import Session
from core.models.database import EventTable
from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert
from core.schemas.schema import Event, CreateEvent, UpdateEvent, DeleteEvent, Set, UserEventTime, UserWithEvents,\
    AllUserEvent, FrontComment, PriorityEvent


map_tags = {
    'Спорт': 0,
    'Музыка': 1,
    'Учеба': 2,
    'Наука': 3,
    'Развлечения': 4,
    'Соревнования': 5,
    'Олимпиада': 6,
    'Программирование': 7,
    'Праздник': 8,
    'Культура и искусство': 9,
    'Творчество': 10,
    'Университетское': 11,
    'Мастеркласс': 12,
    'Cтажировка': 13,
    'Волонтер': 14,
    'Медиа': 15,
    'Туризм': 16,
    'Медицина': 17,
    'Кино': 18
}


def get_template(user: int = None):
    my_actions = ''
    if user:
        f"""
        ,   (
                SELECT
                    uh.liked
                FROM
                    user_history uh
                WHERE
                    uh.user_id = {user} and
                    uh.event_id = ev.id
            ) "liked"
        ,   (
                SELECT
                    uh.favourited
                FROM
                    user_history uh
                WHERE
                    uh.user_id = {user} and
                    uh.event_id = ev.id
            ) "favourited"
        ,   (
                SELECT
                    uh.subscribed
                FROM
                    user_history uh
                WHERE
                    uh.user_id = {user} and
                    uh.event_id = ev.id
            ) "subscribed"
        """
    # user_can_join = ''
    # if user:
    #     user_can/_join = f"""events.owner <> {user} and {user} not in (SELECT UNNEST(members)) and"""
    return f"""
        SELECT 
            id
        ,   name
        ,   created_at::text
        ,   starts_at::text
        ,   ends_at::text
        ,   description_short::text
        ,   description_html::text
        ,   url
        ,   image_url
        ,   location
        ,   array[
                ST_X(geolocation::geometry),
                ST_Y(geolocation::geometry)
            ]::float[] "geolocation"
        ,   (
                SELECT 
                    ARRAY_AGG(JSON_BUILD_OBJECT('tag_id', tag_id, 'tag_name', tag_name)) 
                FROM
                    events_tags 
                WHERE
                    event_id = ev.id group by event_id
            ) "categories"
        ,   age_limit
        ,   moderation_status
        ,   access_status
        ,   user_id
        ,   priority
        {my_actions}
        FROM 
           events ev
    """


@check_token
def add_event(user: int, session: Session, event: CreateEvent):
    event.user_id = user
    stmt_create = insert(EventTable).values(event.dict()).returning(EventTable)
    stmt_select = select(EventTable).from_statement(stmt_create)
    id = session.execute(stmt_select).scalar().id
    return {'status': 'OK', 'event_id': id}


@check_token
def set_priority(user: int, session: Session, event: PriorityEvent):
    session.execute(f"""
        UPDATE
            events ev
        SET
            priority = not ev.Priority
        WHERE
            ev.user_id = (:user)::bigint AND
            ev.event_id = (:event_id)::bigint
    """, {'user_id': user, 'event_id': event.event_id})


@check_token
def change_event(user: int, session: Session, event: UpdateEvent):
    event.user_id = user
    if event.id:
        if session.query(EventTable).get(event.id):
            event_dict = event.dict()
            event_dict = {key: event_dict[key] for key in event_dict if event_dict[key]}
            stmt_update = update(EventTable).where(EventTable.id==event.id).values(event_dict).returning(EventTable)
            stmt_select = select(EventTable).from_statement(stmt_update)
            id = session.execute(stmt_select).scalar().id
            return {'status': 'OK', 'event_id': id}
        else:
            raise HTTPException(status_code=404, detail="Not found")
    else:
        raise HTTPException(status_code=404, detail="Not found")


@check_token
def delete_event(user: int, session: Session, event: DeleteEvent):
    if exist_event := session.query(EventTable).get(event.id):
        if exist_event.owner == user:
            session.execute(delete(EventTable).where(EventTable.id == event.id))
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        raise HTTPException(status_code=404, detail="Not found")
    return {'status': 'OK', 'event_id': event.id}


def get_params(key: list):
    if len(key) == 2:
        param1, param2 = key
    else:
        param1, param2 = key[0], None
    return param1, param2


def change_stats(func):
    def update_stat(*args, **kwargs):
        session = kwargs.get('session')
        rs = func(*args, **kwargs)
        if not (user_id := kwargs.get('user')) or not kwargs.get('auth', False):
            return rs
        events = [event.id for event in rs]
        old_new = session.execute(f"""
            WITH md AS (
                SELECT
                    data.user_id
                ,   unnest(data.events_id) "event_id"
                ,   TRUE "showed"
                ,   (:opened)::boolean "opened"
                ,   (SELECT uh.user_id IS NOT NULL) "inserted"
                FROM
                    jsonb_to_recordset((:data)::jsonb) as data(
                        user_id bigint,
                        events_id bigint[]
                    )
                LEFT JOIN
                    user_history uh on data.user_id = uh.user_id
            )
            , before as (
                SELECT
                    md.user_id
                ,   md.event_id
                ,   COALESCE(uh.showed, False)"old_showed"
                ,   COALESCE(uh.opened, False) "old_opened" 
                ,   COALESCE(uh.liked, False) "old_liked"
                ,   COALESCE(uh.favourited, FALSE) "old_favourited"
                ,   md.showed
                ,   md.opened
--                 ,   md.liked
--                 ,   md.favourited
                FROM
                    md
                LEFT JOIN
                    user_history uh on md.user_id = uh.user_id and md.event_id = uh.event_id 
            )
            , insert_history as (
                INSERT INTO
                    user_history (user_id, event_id, showed, opened, liked, favourited, date_opened)
                SELECT
                    md.user_id
                ,   md.event_id
                ,   TRUE 
                ,   md.opened
                ,   FALSE
                ,   FALSE
                ,   (current_timestamp)::timestamp
                FROM
                    md
                RETURNING 
                    user_history.user_id
                ,   user_history.event_id
                ,   FALSE "old_showed"
                ,   FALSE "old_opened"
                ,   FALSE "old_liked"
                ,   FALSE "old_favourited"
                ,   showed
                ,   opened
            )
            , update_history as (
                UPDATE
                    user_history uh
                SET
                    showed = md.showed,
                    opened = (:opened)::boolean
                FROM
                    md
                WHERE
                    uh.user_id = md.user_id AND
                    uh.event_id = md.event_id
            )
            SELECT
                before.*
            FROM
                before
            UNION
            SELECT
                insert_history.*
            FROM
                insert_history
        """, {
            'opened': kwargs.get('id') is not None,
            'data': json.dumps([{'user_id': user_id, 'events_id': events}], default=str)}
        ).fetchall()

        return rs

    return update_stat


@check_token
# @change_stats
def read_events(session: Session, *args, **kwargs):
    id = kwargs.get('id')
    query = get_template()
    if id:
        query += f"""WHERE ev.id = {id} ORDER BY ev.starts_at desc """
        result = [Event(**rec._mapping) for rec in session.execute(query).all()]
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Not found")

    else:
        name = kwargs.get('name')
        created_at = kwargs.get('created_at')
        starts_at = kwargs.get('start_at')
        org_id = kwargs.get('org_id')
        user_id = kwargs.get('user_id')
        age_limit = kwargs.get('age_limit')
        categories = kwargs.get('categories')
        sort = kwargs.get('sort')
        priority = kwargs.get('priority')
        filters = []

        if priority:
            filters.append(f"""
                ev.priority = True
            """)

        if age_limit:
            filters.append(f"""
                ev.age_limit >= {age_limit}
            """)

        if categories:
            filters.append(f"""
                ARRAY{categories} && (
                    SELECT 
                        array_agg(tag_id) 
                    FROM
                        events_tags
                    WHERE
                        event_id = ev.id
                    )
            """)

        if name:
            filters.append(f"""
                ev.name ILIKE '%{str(name)}%'
            """)

        if org_id:
            filters.append(f"""
                ev.id in (
                    SELECT
                        orgev.event_id
                    FROM
                        org_events orgev
                    WHERE
                        orgev.org_id = ({org_id})::bigint
                )
            """)

        if user_id:
            filters.append(f"""
                ev.user_id = ({user_id})::bigint
            """)

        if created_at:
            start_from, start_to = get_params(created_at)
            filters.append(f"""
                (ev.created_at)::timestamptz >= '{str(start_from)}'::timestamptz
            """)
            if start_to:
                filters.append(f"""
                    (ev.created_at)::timestamptz <= '{str(start_to)}'::timestamptz  
                """)

        if starts_at:
            start_from, start_to = get_params(created_at)
            filters.append(f"""
                (ev.starts_at)::timestamptz >= '{str(start_from)}'::timestamptz
            """)
            if start_to:
                filters.append(f"""
                    (ev.starts_at)::timestamptz <= '{str(start_to)}'::timestamptz  
                """)

        if filters:
            query += "WHERE "
            iterations = len(filters)
            for i in range(iterations):
                query += filters[i]
                if i != iterations - 1:
                    query += "and "

        if sort:
            sort = sort.split('|')
            if len(sort) == 2:
                column, order = sort
            else:
                column, order = sort[0], 'asc'
            query += f"ORDER BY {column} {order}"

        else:
            query += f""" ORDER BY ev.starts_at """

    return [Event(**rec._mapping) for rec in session.execute(query).all()]


@check_token
def read_my_events(user: int, session: Session):
    return read_user_events(session, user)


def read_user(user: str, session: Session):
    if user.isdigit():
        user = session.execute(f"""
            SELECT 
                id, username, name, surname, last_name, sex, email, icon_id  
            FROM users WHERE id = '{user}'
        """).all()
    else:
        user = session.execute(f"""
            SELECT 
                id, username, name, surname, last_name, sex, email, icon_id
            FROM users WHERE username = '{user}'
        """).all()
    if user:
        user = user[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    events = read_user_events(session, user.id)
    return UserWithEvents(events=events, **user._mapping)
    # return UserWithEvents(id=user.id, username=user.username, name=user.name, surname=user.surnevents=events, **)


def read_user_events(session: Session, user: int = None):
    date, time = str(datetime.datetime.now()).split(' ')
    query = get_template(user)
    query += f"""
        WHERE events."owner" = {user} or {user} = ANY(events."members") 
        ORDER BY events."date" desc, events."start_time" desc
    """
    rs = session.execute(query).all()
    owner_future = []
    owner_past = []
    member_future = []
    member_past = []
    for rec in rs:
        if rec.owner == user:
            if rec.date > date:
                owner_future.append(Event(**rec._mapping))
            elif rec.date == date:
                if rec.start_time > time:
                    owner_future.append(Event(**rec._mapping))
                else:
                    owner_past.append(Event(**rec._mapping))
            else:
                owner_past.append(Event(**rec._mapping))
        else:
            if rec.date > date:
                member_future.append(Event(**rec._mapping))
            elif rec.date == date:
                if rec.start_time > time:
                    member_future.append(Event(**rec._mapping))
                else:
                    member_past.append(Event(**rec._mapping))
            else:
                member_past.append(Event(**rec._mapping))

    return AllUserEvent(
        owner=UserEventTime(future_event=owner_future, past_event=owner_past),
        member=UserEventTime(future_event=member_future, past_event=member_past)
    )


def read_sets(session: Session):
    rs = json.dumps([{'@Id': value, "name": key} for key, value in map_tags.items()], default=str)
    return [Set(**row._mapping) for row in session.execute(f"""
                WITH mat_data as (
                    SELECT
                        "@Id"
                    ,   "name"
                    ,   True as "event"
                    FROM 
                        jsonb_to_recordset('{rs}'::jsonb) as md(
                            "@Id" smallint
                        ,   "name" text
                        )
                    JOIN
                        events on md."@Id" = ANY(events.tags)
                )
                , event_count as (
                    SELECT
                        mat_data."@Id"
                    ,   COUNT(*) as "event_count"
                    FROM
                        mat_data
                    GROUP BY 
                        mat_data."@Id"
                )
                SELECT DISTINCT
                    event_count."@Id" as "id"
                ,   mat_data."name"
                ,   event_count."event_count"
                FROM
                    event_count
                JOIN
                    mat_data on event_count."@Id" = mat_data."@Id"
                ORDER BY 
                    event_count."event_count" desc
                ,   event_count."@Id" asc
            """).all()]


@check_token
def like_dislike_event(user: int, id: int, session: Session):
    session.execute(f"""
        WITH md AS (
            SELECT
                data.user_id
            ,   data.event_id
            ,   (SELECT uh.user_id IS NOT NULL) "inserted"
            ,   COALESCE(uh.liked, FALSE) "liked"
            FROM
                jsonb_to_recordset((:data)::jsonb) as data(
                    user_id bigint,
                    event_id bigint
                )
            LEFT JOIN
                user_history uh on data.user_id = uh.user_id and data.event_id = uh.event_id
        )
        , insert_history as (
            INSERT INTO 
                user_history (user_id, event_id, liked)
            SELECT
                md.user_id
            ,   md.event_id
            ,   not md.liked
            FROM
                md
            WHERE
                md.inserted IS FALSE
        )
        UPDATE
            user_history uh
        SET
            liked = not md.liked
        FROM
            md
        WHERE
            uh.user_id = md.user_id AND
            uh.event_id = md.event_id
    """, {'data': json.dumps([{'user_id': user, 'event_id': id}], default=str)})
    return {'status': 'OK', 'id': id}


@check_token
def subscribe_event(id: int, user: int, session: Session):
    result = session.execute(f"""
        WITH md AS (
            SELECT
                data.user_id
            ,   data.event_id
            ,   (SELECT uh.user_id IS NOT NULL) "inserted"
            ,   COALESCE(uh.subscribed, FALSE) "subscribed"
            FROM
                jsonb_to_recordset((:data)::jsonb) as data(
                    user_id bigint,
                    event_id bigint
                )
            LEFT JOIN
                user_history uh on data.user_id = uh.user_id and data.event_id = uh.event_id
        )
        , insert_history as (
            INSERT INTO 
                user_history (user_id, event_id, subscribed)
            SELECT
                md.user_id
            ,   md.event_id
            ,   not md.subscribed
            FROM
                md
            WHERE
                md.inserted IS FALSE
        )
        UPDATE
            user_history uh
        SET
            subscribed = not md.subscribed
        FROM
            md
        WHERE
            uh.user_id = md.user_id AND
            uh.event_id = md.event_id
    """, {'data': json.dumps([{'user_id': user, 'event_id': id}], default=str)})
    if result:
        return {'status': 'OK', 'id': id}
    else:
        return {'status': 'ERROR', 'id': id}


@check_token
def favourite_event(id: int, user: int, session: Session):
    result = session.execute(f"""
        WITH md AS (
            SELECT
                data.user_id
            ,   data.event_id
            ,   (SELECT uh.user_id IS NOT NULL) "inserted"
            ,   COALESCE(uh.favourited, FALSE) "favourited"
            FROM
                jsonb_to_recordset((:data)::jsonb) as data(
                    user_id bigint,
                    event_id bigint
                )
            LEFT JOIN
                user_history uh on data.user_id = uh.user_id and data.event_id = uh.event_id
        )
        , insert_history as (
            INSERT INTO 
                user_history (user_id, event_id, favourited)
            SELECT
                md.user_id
            ,   md.event_id
            ,   not md.favourited
            FROM
                md
            WHERE
                md.inserted IS FALSE
        )
        UPDATE
            user_history uh
        SET
            favourited = not md.favourited
        FROM
            md
        WHERE
            uh.user_id = md.user_id AND
            uh.event_id = md.event_id
    """, {'data': json.dumps([{'user_id': user, 'event_id': id}], default=str)})
    if result:
        return {'status': 'OK', 'id': id}
    else:
        return {'status': 'ERROR', 'id': id}


@check_token
def write_comment(user: int, comment: FrontComment, session: Session):
    user = session.execute(f"""
        SELECT username FROM users WHERE id = '{user}'
    """).one()

    session.execute(f"""
        UPDATE
            events
        SET
            comments = CASE
                            WHEN comments is null then
                                ARRAY[ARRAY['{user.username}',  '{comment.comment}']]
                            ELSE
                                array_cat(comments,  ARRAY[ARRAY['{user.username}',  '{comment.comment}']])
                        END
        WHERE
            id = {comment.event_id}
    """)
    return {'status': 'OK', 'event_id': comment.event_id}
