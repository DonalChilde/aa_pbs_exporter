####################################################
#                                                  #
#    src/snippets/messages/publisher_consumer.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-14T04:34:10-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from typing import Dict, Sequence


class MessageConsumer:
    """
    A consumer of messages.

    Subclass this, and override `consume_messages` to provide custom behavior.
    """

    def __init__(self) -> None:
        pass

    def consume_message(
        self,
        msg: str,
        *,
        category: str = "",
        level: int | None = None,
        extras: Dict | None = None,
    ):
        """
        Message consumer, usually called from a :class:`MessagePublisher`

        Consumes a message in a particular way, eg. print to stdout

        Args:
            msg: The message to be consumed.
            category: A string used to differentiate messages. Defaults to "".
            level: An optional int used to differentiate messages. Can correspond to
                log levels. Defaults to None.
            extras: A optional Dict which can hold extra information. Defaults to None.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError("Subclass and override this method.")


class MessagePublisher:
    """
    Holds message consumers, and publishes messages to them.

    Args:
        consumers: The message consumers.
    """

    def __init__(self, consumers: Sequence[MessageConsumer]) -> None:

        self.consumers = list(consumers)

    def publish_message(
        self,
        msg: str,
        *,
        category: str = "",
        level: int | None = None,
        extras: Dict | None = None,
    ):
        """
        Publish a message to consumers.

        Args:
            msg: The message to be consumed.
            category: A string used to differentiate messages. Defaults to "".
            level: An optional int used to differentiate messages. Can correspond to
                log levels. Defaults to None.
            extras: A optional Dict which can hold extra information. Defaults to None.
        """
        for consumer in self.consumers:
            consumer.consume_message(msg, category=category, level=level, extras=extras)


class StdoutConsumer(MessageConsumer):
    """
    Print messages to stdout.
    """

    def consume_message(
        self,
        msg: str,
        *,
        category: str = "",
        level: int | None = None,
        extras: Dict | None = None,
    ):
        print(
            f"Category: {category}\nLevel: {level}\nMessage: {msg}\nExtras: {extras!r}"
        )
