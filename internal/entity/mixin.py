import sqlalchemy as sa
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class TimestampMixin(object):

    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, onupdate=sa.func.now())
    deleted_at = sa.Column(sa.DateTime)
