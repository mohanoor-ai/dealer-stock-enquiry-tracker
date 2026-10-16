"""Database-backed limits shared across workers; no raw email/IP keys retained."""
import hashlib
import time
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from backend_v2.models import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from backend_v2.service import Problem


class Bucket(Base):
    __tablename__ = 'rate_buckets_v2'
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    window: Mapped[int] = mapped_column(Integer, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)


def consume(sessions, purpose, identity, limit, seconds):
    window = int(time.time()) // seconds
    key = hashlib.sha256((purpose + ':' + identity).encode()).hexdigest()
    with sessions.begin() as db:
        try:
            with db.begin_nested():
                db.add(Bucket(key=key, window=window, count=0))
                db.flush()
        except IntegrityError:
            pass
        db.execute(update(Bucket).where(Bucket.key == key, Bucket.window < window).values(window=window, count=0))
        result = db.execute(update(Bucket).where(Bucket.key == key, Bucket.window == window, Bucket.count < limit).values(count=Bucket.count + 1))
        if result.rowcount != 1:
            raise Problem(429, 'quota', 'Request limit reached. Try again later.')
