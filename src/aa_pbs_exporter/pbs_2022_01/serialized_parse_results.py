from pydantic import BaseModel

from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import ParseResultProtocol

class SerializableParseResult(BaseModel):
    current_state:str
    parsed_data:dict

class SerializableParseResults(BaseModel):
    results:list[SerializableParseResult]


def deserialize_parse_result(serialized:SerializableParseResult)->ParseResultProtocol:
    pass