import datetime
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geography
from sqlalchemy import Column, ForeignKey, Integer, String, Identity, Date, Time, Float, Boolean, DateTime


SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/hackaton'
db = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=db, autocommit=False)
Base = declarative_base()


class UserTable(Base):
    __tablename__ = "users"
    id = Column(Integer, Identity(start=1), primary_key=True, unique=True)
    username = Column(String, nullable=True, unique=True)
    name = Column(String, nullable=True)
    password = Column(String, nullable=False)
    surname = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    sex = Column(Integer, nullable=True)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True, unique=True)
    token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    image_url = Column(String, nullable=True)

    def dict(self):
        return {
            rec.name: getattr(self, rec.name)
            if not isinstance(getattr(self, rec.name), datetime.date)
               and not isinstance(getattr(self, rec.name), datetime.time)
            else str(getattr(self, rec.name))
            for rec in self.__table__.columns
        }


class OrganizationTable(Base):
    __tablename__ = "organizations"
    id = Column(Integer, Identity(start=1), primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    owner = Column(Integer, ForeignKey("users.id"), nullable=True)
    image_url = Column(String, nullable=True)
    url = Column(String, nullable=True)
    subdomain = Column(String, nullable=True)


class OrgUserTable(Base):
    __tablename__ = "org_to_users"
    # id = Column(Integer, Identity(start=1), primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    __mapper_args__ = {
        "primary_key": [org_id, user_id]
    }


class OrgEventTable(Base):
    __tablename__ = "org_events"
    org_id = Column(Integer, ForeignKey("organizations.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    __mapper_args__ = {
        "primary_key": [org_id, event_id]
    }


class EventTable(Base):
    __tablename__ = "events"
    id = Column(Integer, Identity(start=1), primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    starts_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)
    description_short = Column(String, nullable=False)
    description_html = Column(String, nullable=True)
    url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    location = Column(String, nullable=True)
    geolocation = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    age_limit = Column(Integer, nullable=True)
    moderation_status = Column(String, nullable=True)
    access_status = Column(String, nullable=True)
    ext_id = Column(String, nullable=True)
    priority = Column(Boolean, nullable=False, server_default='False')
    user_id = Column(Integer, nullable=False, server_default='3')

    # date = Column(Date, nullable=False)
    # count_people = Column(Integer, nullable=False)
    # start_time = Column(Time, nullable=False)
    # address = Column(String)
    # icon_id = Column(String)
    # owner = Column(Integer, ForeignKey("users.id"))
    # tags = Column(ARRAY(Integer))
    # likes = Column(Integer, default=0)
    # dislikes = Column(Integer, default=0)
    # members = Column(ARRAY(Integer), default=[])
    # comments = Column(ARRAY(String), default=[])

    def dict(self):
        return {
            rec.name: getattr(self, rec.name)
            if not isinstance(getattr(self, rec.name), datetime.date)
               and not isinstance(getattr(self, rec.name), datetime.time)
            else str(getattr(self, rec.name))
            for rec in self.__table__.columns
        }


class EventsTags(Base):
    __tablename__ = "events_tags"
    event_id = Column(Integer, ForeignKey("events.id"))
    tag_id = Column(Integer, nullable=False)
    tag_name = Column(String, nullable=False)
    __mapper_args__ = {
        "primary_key": [event_id, tag_id]
    }


class EventStat(Base):
    __tablename__ = "event_stat"
    event_id = Column(Integer, ForeignKey("events.id"))
    shows = Column(Integer, nullable=False, default=0)
    open = Column(Integer, nullable=False, default=0)
    likes = Column(Integer, nullable=False, default=0)
    favourites = Column(Integer, nullable=False, default=0)
    date = Column(Date, nullable=False)
    __mapper_args__ = {
        "primary_key": [event_id, date]
    }


class UserHistory(Base):
    __tablename__ = "user_history"
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    showed = Column(Boolean, nullable=False, server_default='False')
    opened = Column(Boolean, nullable=False, server_default='False')
    liked = Column(Boolean, nullable=False, server_default='False')
    favourited = Column(Boolean, nullable=False, server_default='False')
    subscribed = Column(Boolean, nullable=False, server_default='False')
    date_opened = Column(DateTime, nullable=True)
    __mapper_args__ = {
        "primary_key": [user_id, event_id]
    }


try:
    db.connect()
    print(f"Connection {db.url}")
except Exception as e:
    print(f"Database conn error: {e}")


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.commit()
        session.close()
# add fixtures
