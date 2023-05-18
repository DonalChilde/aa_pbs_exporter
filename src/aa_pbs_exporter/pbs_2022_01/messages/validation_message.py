class ValidationMessage:
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def produce_message(self) -> str:
        return self.msg

    def __str__(self) -> str:
        return self.msg

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(msg={self.msg})"
