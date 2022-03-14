import sqlalchemy as sa

from . import Base

__all__ = ["Application"]


class Application(Base):

    __table_args__ = (
        sa.UniqueConstraint("phone"),
        sa.UniqueConstraint("email"),
    )

    phone = sa.Column(sa.String(255), index=True)
    email = sa.Column(sa.String(255), index=True)
    text = sa.Column(sa.Text)
