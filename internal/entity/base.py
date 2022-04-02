import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base(object):

    __name__: str
    metadata: MetaData

    @declared_attr
    def __tablename__(cls):  # noqa: N805
        return cls.__name__.lower()

    id = sa.Column(sa.Integer, primary_key=True, index=True)
