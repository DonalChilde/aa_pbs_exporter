from aa_pbs_exporter.pbs_2022_01.models.parse_result import ParseResult


class ParseResultMessage:
    def __init__(self, parse_result: ParseResult) -> None:
        self.parse_result = parse_result

    def produce_message(self) -> str:
        return str(self.parse_result)
