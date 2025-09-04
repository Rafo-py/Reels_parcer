from sqlalchemy import BigInteger, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)

    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=True, unique=True)
    tg_username: Mapped[str] = mapped_column(String, nullable=True)
    region: Mapped[str] = mapped_column(String, nullable=True)
    rq_count: Mapped[int] = mapped_column(BigInteger, default=0)


class History(Base):
    __tablename__ = 'history'

    id: Mapped[int] = mapped_column(primary_key=True)

    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    username_parsed: Mapped[str] = mapped_column(String, nullable=False)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
