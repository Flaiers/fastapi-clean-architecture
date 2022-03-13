from sqlalchemy.ext.declarative import as_declarative, declared_attr
import sqlalchemy as sa


@as_declarative()
class Base:

    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
