from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Identity, Date, Time


SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/test'
Base = declarative_base()


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.commit()
        session.close()


class UserTable(Base):
    __tablename__ = "users"
    id = Column(Integer, Identity(start=1), primary_key=True, unique=True)
    username = Column(String(25), nullable=True, unique=True)
    name = Column(String(), nullable=False)
    password = Column(String(), nullable=False)
    surname = Column(String(), nullable=False)
    last_name = Column(String())
    sex = Column(String(), nullable=False)
    email = Column(String(), nullable=False, unique=True)
    token = Column(String(), nullable=False)
    refresh_token = Column(String(), nullable=False)
    organization = relationship("OrganizationTable", secondary="org_to_users")


class OrganizationTable(Base):
    __tablename__ = "organizations"
    id = Column(Integer, Identity(start=1), primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    owner = relationship("UserTable", secondary="org_to_users")


class OrgUserTable(Base):
    __tablename__ = "org_to_users"
    id = Column(Integer, Identity(start=1), primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))


class EventTable(Base):
    __tablename__ = "events"
    id = Column(Integer, Identity(start=1), primary_key=True)
    title = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    count_people = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    address = Column(String)
    icon_id = Column(String)
    owner = Column(Integer, ForeignKey("users.id"))
    # tags = Column()


try:
    db = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(db)
    SessionLocal = sessionmaker(bind=db, autocommit=False)
    db.connect()
    print(f"Connection {db.url}")
except Exception as e:
    print(f"Database conn error: {e}")