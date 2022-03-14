import sqlalchemy as sa
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:

    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:  # noqa: N805
        return "{0}s".format(cls.__name__.lower())

    id = sa.Column(sa.Integer, primary_key=True, index=True)
