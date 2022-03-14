import enum


class OrderDirection(str, enum.Enum):  # noqa: WPS600

    asc = "asc"
    desc = "desc"
