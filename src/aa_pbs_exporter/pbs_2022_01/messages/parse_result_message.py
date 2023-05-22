from aa_pbs_exporter.pbs_2022_01.models.parse_result import ParseResult


class ParseResultMessage:
    def __init__(self, parse_result: ParseResult) -> None:
        self.parse_result = parse_result

    def produce_message(self) -> str:
        return str(self.parse_result)

    def __str__(self) -> str:
        return self.produce_message()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(parse_result={self.parse_result!r})"
