####################################################
#                                                  #
#          src/snippets/string/indent.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2023-05-22T06:53:34-07:00            #
# Last Modified: 2023-05-22T14:02:07.321643+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################


def indent(txt: str, indent_level: int, *, indent_char: str = "\t") -> str:
    """
    Indents text by adding leading characters to each line.

    Args:
        txt: The string to be indented.
        indent_level: Level of indentation. 0 returns txt unchanged.
        indent_char: Characters used for indentation. Defaults to "\t".

    Returns:
        _description_
    """
    if indent_level == 0:
        return txt
    txt = f"{indent_char*indent_level}{txt}"
    txt = txt.replace("\n", f"\n{indent_char*indent_level}")
    return txt
