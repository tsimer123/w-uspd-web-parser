from collections.abc import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import db_name

# load_dotenv()

# username_db = os.getenv('username_db')
# password_db = os.getenv('password_db')
# host_db = os.getenv('host_db')
# port_db = os.getenv('port_db')
# database = os.getenv('database')

url_object = URL.create(
    'sqlite+aiosqlite',
    database=db_name,
)

# engine = create_engine(url_object)


async_engine = create_async_engine(
    url=url_object,
    # echo=True,
)


async_session_factory = async_sessionmaker(async_engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
