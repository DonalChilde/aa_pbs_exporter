from io import TextIOWrapper
from typing import Callable

from aa_pbs_exporter.snippets import messages
from aa_pbs_exporter.snippets.string.indent import indent


def parse_sieve() -> Callable[[messages.Message], bool]:
    return messages.category_sieve("parse")


def translation_sieve() -> Callable[[messages.Message], bool]:
    return messages.category_sieve("translation")


def validation_sieve() -> Callable[[messages.Message], bool]:
    return messages.category_sieve("validation")


def status_sieve() -> Callable[[messages.Message], bool]:
    return messages.category_sieve("status")


def std_out_sieve() -> Callable[[messages.Message], bool]:
    return messages.category_sieve("foo")  # FIXME needs multiple sieve function


def indent_message(msg: messages.Message) -> str:
    if msg.level is None:
        level = 0
    else:
        level = msg.level
    return indent(msg.produce_message(), level)


def init_publisher(
    parse_fp: TextIOWrapper | None = None,
    translation_fp: TextIOWrapper | None = None,
    validation_fp: TextIOWrapper | None = None,
    std_out: bool = True,
) -> messages.MessagePublisher:
    msg_pub = messages.MessagePublisher([])
    parse = messages.PrintMessengeListener(
        sieve=parse_sieve(), formatter=indent_message, file=parse_fp
    )
    translation = messages.PrintMessengeListener(
        sieve=translation_sieve(), formatter=indent_message, file=translation_fp
    )
    validation = messages.PrintMessengeListener(
        sieve=validation_sieve(), formatter=indent_message, file=validation_fp
    )
    msg_pub.listeners.extend((parse, translation, validation))
    if std_out:
        msg_pub.listeners.append(
            messages.PrintMessengeListener(
                sieve=status_sieve(), formatter=indent_message
            )
        )

    return msg_pub
