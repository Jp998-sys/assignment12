# tests/conftest.py

import logging
from typing import Generator, Dict, List

import pytest
from faker import Faker
from sqlalchemy.orm import Session

from app.database import Base, get_engine, get_sessionmaker
from app.models.user import User
from app.config import settings
from app.database_init import init_db, drop_db


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


fake = Faker()
Faker.seed(12345)

logger.info(f"Using database URL: {settings.DATABASE_URL}")

test_engine = get_engine(database_url=settings.DATABASE_URL)
TestingSessionLocal = get_sessionmaker(engine=test_engine)


def create_fake_user() -> Dict[str, str]:
    return {
        "username": fake.unique.user_name(),
        "email": fake.unique.email(),
        "password_hash": User.hash_password("SecurePass123!")
    }


@pytest.fixture(scope="session", autouse=True)
def setup_test_database(request):
    logger.info("Setting up test database...")

    Base.metadata.drop_all(bind=test_engine)
    logger.info("Dropped all existing tables.")

    Base.metadata.create_all(bind=test_engine)
    logger.info("Created all tables based on models.")

    init_db()
    logger.info("Initialized the test database with initial data.")

    yield

    preserve_db = request.config.getoption("--preserve-db")
    if preserve_db:
        logger.info("Skipping drop_db due to --preserve-db flag.")
    else:
        logger.info("Cleaning up test database...")
        drop_db()
        logger.info("Dropped test database tables.")

@pytest.fixture
def db_session(request) -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        preserve_db = request.config.getoption("--preserve-db")
        if not preserve_db:
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
        session.close()


@pytest.fixture
def fake_user_data() -> Dict[str, str]:
    return create_fake_user()

@pytest.fixture
def test_user(db_session: Session) -> User:
    user_data = create_fake_user()
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def seed_users(db_session: Session, request) -> List[User]:
    try:
        num_users = request.param
    except AttributeError:
        num_users = 5

    users = []
    for _ in range(num_users):
        user_data = create_fake_user()
        user = User(**user_data)
        users.append(user)
        db_session.add(user)

    db_session.commit()
    return users

def pytest_addoption(parser):
    parser.addoption(
        "--preserve-db",
        action="store_true",
        default=False,
        help="Keep test database after tests."
    )