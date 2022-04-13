import sqlalchemy as sa

from internal.entity.base import Base
from internal.entity.mixin import TimestampMixin


class Application(TimestampMixin, Base):

    __table_args__ = (
        sa.UniqueConstraint('phone'),
        sa.UniqueConstraint('email'),
    )

    phone = sa.Column(sa.String(255), index=True, nullable=False)
    email = sa.Column(sa.String(255), index=True, nullable=False)
    text = sa.Column(sa.Text, nullable=False)
