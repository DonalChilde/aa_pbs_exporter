####################################################
#                                                  #
# src/snippets/code_generation/dataclass_repr_mixin.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-02T12:41:19-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from dataclasses import fields


class DataclassReprMixin:
    def __repr__(self):
        # enhanced from Fluent Python 2ed. p189
        cls = self.__class__
        cls_name = cls.__name__
        # dataclass version
        field_names = (field.name for field in fields(cls))
        indent = " " * 2
        rep = [f"{cls_name}("]
        for field_ in field_names:
            value = getattr(self, field_)
            if isinstance(value, DataclassReprMixin):
                subdent = f"\n{indent}{indent}"
            else:
                subdent = ""
            rep.append(f"{indent}{field_} = {subdent}{value!r}")
        rep.append(")")
        return "\n".join(rep)
