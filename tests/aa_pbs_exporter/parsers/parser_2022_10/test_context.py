from aa_pbs_exporter.parsers.parser_2022_10.line_parser import ParseContext


class ParseContextTest(ParseContext):
    def __init__(self, file_name: str) -> None:
        super().__init__(file_name)
        self.parsed_data = None

    def handle_parse(self, data):
        self.parsed_data = data
