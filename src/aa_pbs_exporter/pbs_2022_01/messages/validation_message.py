class ValidationMessage:
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def produce_message(self) -> str:
        return self.msg
