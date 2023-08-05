from uuid import UUID


class ValidationError:
    def __init__(self, msg: str, uuid: UUID | None) -> None:
        self.msg = msg
        self.uuid = uuid

    def __str__(self) -> str:
        return f"{self.msg}, uuid={self.uuid}"
