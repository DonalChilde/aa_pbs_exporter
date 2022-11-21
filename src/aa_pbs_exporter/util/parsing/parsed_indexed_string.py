####################################################
#                                                  #
# src/snippets/parsing/parsed_indexed_string.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-10T15:15:11-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from dataclasses import dataclass, fields

from .indexed_string import IndexedString


@dataclass
class ParsedIndexedString:
    """Base class for a dataclass that represents the parse result of a string."""

    source: IndexedString

    def __str__(self) -> str:
        return self._indent_str()

    def _indent_str(self, indent: str = "", indent_level: int = 0) -> str:
        cls = self.__class__
        cls_name = cls.__name__
        field_names = [field.name for field in fields(cls)]
        source = getattr(self, "source", "source field not defined.")
        field_names.remove("source")
        beginning = f"{indent*indent_level}{source!s}\n{indent*indent_level}{cls_name}("
        field_strings = []
        for field_ in field_names:
            value = getattr(self, field_)
            field_strings.append(f"{field_} = {value!r}")
        middle = ", ".join(field_strings)
        end = ")"
        return f"{beginning}{middle}{end}"
