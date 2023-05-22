# ####################################################
# #                                                  #
# # src/snippets/indexed_string/state_parser/result_handler.py
# #                                                  #
# ####################################################
# # Created by: Chad Lowe                            #
# # Created on: 2023-04-16T08:06:21-07:00            #
# # Last Modified: 2023-04-23T17:57:50.057400+00:00  #
# # Source: https://github.com/DonalChilde/snippets  #
# ####################################################


# from io import TextIOWrapper
# from typing import Sequence

# from aa_pbs_exporter.snippets.indexed_string.state_parser.state_parser_protocols import (
#     ParseResultProtocol,
#     ResultHandlerProtocol,
# )


# # TODO make example function that saves all odd numbered input lines to a file.
# class ParseResultHandler(ResultHandlerProtocol):
#     def __init__(self) -> None:
#         pass

#     def initialize(self, ctx: dict | None = None):
#         """Called before the first parse attempt of a parse job."""
#         _ = ctx

#     def handle_result(
#         self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
#     ):
#         raise NotImplementedError

#     def finalize(self, ctx: dict | None = None):
#         """Called after the last chunk of data is parsed."""
#         _ = ctx


# class MultipleResultHandler(ParseResultHandler):
#     def __init__(self, result_handlers: Sequence[ResultHandlerProtocol]) -> None:
#         """
#         Contain multiple result handlers.

#         Used to pass a parse result to multiple handlers in sequence.

#         Args:
#             result_handlers: The result handlers.
#         """
#         self.handlers = list(result_handlers)

#     def initialize(self, ctx: dict | None = None):
#         """Called before the first parse attempt of a parse job."""
#         for handler in self.handlers:
#             handler.initialize(ctx)

#     def handle_result(
#         self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
#     ):
#         """Passes the parse result to multiple handlers in sequence."""
#         for handler in self.handlers:
#             handler.handle_result(parse_result=parse_result, ctx=ctx, **kwargs)

#     def finalize(self, ctx: dict | None = None):
#         """Called after the last chunk of data is parsed."""
#         for handler in self.handlers:
#             handler.finalize(ctx)


# class ParseResultToFile(ParseResultHandler):
#     def __init__(self, writer: TextIOWrapper, record_separator: str = "") -> None:
#         """
#         Save the parse_result to an opened text file.

#         Args:
#             writer: An opened text file.
#             record_separator: A string written between records, eg. `\n`. Defaults to to ''.
#         """
#         self.writer = writer
#         self.record_separator = record_separator

#     def handle_result(
#         self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
#     ):
#         self.writer.write(
#             self.result_to_txt(parse_result=parse_result, ctx=ctx, **kwargs)
#         )
#         if self.record_separator:
#             self.writer.write(self.record_separator)

#     def result_to_txt(
#         self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
#     ) -> str:
#         """Return the string representation of a ParseResult."""
#         _ = kwargs, ctx
#         return f"{parse_result!s}"


# class ParseResultReprToFile(ParseResultToFile):
#     def result_to_txt(
#         self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
#     ) -> str:
#         _ = kwargs, ctx
#         return f"{parse_result!r}"


# class ParsedDataToFile(ParseResultToFile):
#     def result_to_txt(
#         self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
#     ) -> str:
#         return f"{parse_result.parsed_data!s}"


# class ParsedDataReprToFile(ParseResultToFile):
#     def result_to_txt(
#         self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
#     ) -> str:
#         return f"{parse_result.parsed_data!r}"


# # class ParseResultSaveToTextFileHandler:
# #     def __init__(
# #         self, writer: TextIOWrapper, record_separator: str = "", as_repr: bool = False
# #     ) -> None:
# #         """
# #         Save the parse result to an opened text file.

# #         Args:
# #             writer: An opened text file.
# #             record_separator: A string written between records, eg. `\n`. Defaults to to ''.
# #             as_repr: Output as repr(value)
# #         """
# #         self.writer = writer
# #         self.record_separator = record_separator
# #         self.as_repr = as_repr

# #     def initialize(self, ctx: dict | None = None):
# #         """Called before the first parse attempt of a parse job."""
# #         pass

# #     def handle_result(
# #         self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
# #     ):
# #         """Save the parse result to a text file as str(parse_result)."""
# #         _ = kwargs, ctx
# #         if self.as_repr:
# #             self.writer.write(f"{parse_result!r}")
# #         else:
# #             self.writer.write(f"{parse_result}")
# #         if self.record_separator:
# #             self.writer.write(self.record_separator)

# #     def finalize(self, ctx: dict | None = None):
# #         """Called after the last chunk of data is parsed."""
# #         pass


# # class ParsedDataSaveToTextFileHandler:
# #     def __init__(
# #         self, writer: TextIOWrapper, record_separator: str = "", as_repr: bool = False
# #     ) -> None:
# #         """
# #         Save the parse_result.parsed_data to an opened text file.

# #         Args:
# #             writer: An opened text file.
# #             record_separator: A string written between records, eg. `\n`. Defaults to to ''.
# #             as_repr: Output as repr(value)
# #         """
# #         self.writer = writer
# #         self.record_separator = record_separator
# #         self.as_repr = as_repr

# #     def initialize(self, ctx: dict | None = None):
# #         """Called before the first parse attempt of a parse job."""
# #         pass

# #     def handle_result(
# #         self, parse_result: ParseResultProtocol, ctx: dict | None = None, **kwargs
# #     ):
# #         """Save the parse_result.parsed_data to a text file."""
# #         _ = kwargs, ctx
# #         if self.as_repr:
# #             self.writer.write(f"{parse_result.parsed_data!r}")
# #         else:
# #             self.writer.write(f"{parse_result.parsed_data}")
# #         if self.record_separator:
# #             self.writer.write(self.record_separator)

# #     def finalize(self, ctx: dict | None = None):
# #         """Called after the last chunk of data is parsed."""
# #         pass
