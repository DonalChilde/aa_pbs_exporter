####################################################
#                                                  #
#        src/snippets/file/clean_filename.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-14T08:59:22-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Set

INVALID_LINUX = {"/", "\0"}
INVALID_WINDOWS = {"<", ">", ":", '"', "/", "\\", "|", "?", "*"}

# https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap03.html
# 3.282 Portable Filename Character Set
POSIX_PORTABLE = set(
    (
        "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z "
        "a b c d e f g h i j k l m n o p q r s t u v w x y z "
        "0 1 2 3 4 5 6 7 8 9 . _ -"
    ).split()
)


def clean_filename_invalid(
    file_name: str, invalid_chars: Set[str] | None = None, replace_with: str = "_"
) -> str:
    """
    Check against a set of invalid characters, and replace them with a valid one.

    Args:
        file_name: The string to be checked for valid characters.
        invalid_chars: The set of invalid characters. If None, defaults to
            `INVALID_WINDOWS`.
        replace_with: Replace invalid characters with this character. It must not
            be one of the invalid characters. Defaults to "_".

    Raises:
        ValueError: `replace_with` must not be in the set of invalid characters.

    Returns:
        The cleaned file name.
    """
    if invalid_chars is None:
        invalid_chars = INVALID_WINDOWS
    if replace_with in invalid_chars:
        raise ValueError(
            f"replace_with: {replace_with} must not be in the set of invalid "
            f"characters: {invalid_chars!r}"
        )
    for char in invalid_chars:
        if char in file_name:
            file_name = file_name.replace(char, replace_with)
    return file_name


def clean_filename_valid(
    file_name: str, valid_chars: Set[str] | None = None, replace_with: str = "_"
) -> str:
    """
    Ensure a file name only contains characters from a set of valid characters.

    Invalid characters are replaced by the `replace_with` value. Characters are
    checked one at a time, with one pass through the whole string.

    Args:
        file_name: The string to be checked for valid characters.
        valid_chars: The set of valid characters. If None, defaults to `POSIX_PORTABLE`.
        replace_with: Replace invalid characters with this single character. It must
            be one of the valid characters. Defaults to "_".

    Raises:
        ValueError: `replace_with` must be in the set of valid characters.

    Returns:
        The cleaned file name.
    """

    if valid_chars is None:
        valid_chars = POSIX_PORTABLE
    if replace_with not in valid_chars:
        raise ValueError(
            f"replace_with: {replace_with} must be in the set of valid "
            f"characters: {valid_chars!r}"
        )
    chars = list(file_name)
    print(len(chars), chars[0])
    for index, char in enumerate(chars):
        if char not in valid_chars:
            chars[index] = replace_with
    return "".join(chars)
