import sqlalchemy as sa

from internal.usecase.utils import consts

from . import Base


class Application(Base):

    __table_args__ = (
        sa.UniqueConstraint("phone"),
        sa.UniqueConstraint("email"),
    )

    phone = sa.Column(sa.String(consts.default_length), index=True)
    email = sa.Column(sa.String(consts.default_length), index=True)
    text = sa.Column(sa.Text)
