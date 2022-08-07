import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.dialects import postgresql as psql
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base(object):

    __name__: str
    metadata: MetaData

    @classmethod
    @declared_attr
    def __tablename__(cls):  # noqa: N805
        return cls.__name__.lower()

    id = sa.Column(
        psql.UUID(as_uuid=True),
        server_default=sa.text('gen_random_uuid()'),
        primary_key=True,
        index=True,
    )
