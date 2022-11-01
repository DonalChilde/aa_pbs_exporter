####################################################
#                                                  #
#          src/snippets/parsing/context.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-10-31T13:56:26-07:00            #
# Last Modified: _iso_date_         #
# Source: https://github.com/DonalChilde/snippets  #
####################################################

from .publisher_consumer import MessagePublisher


class Context:
    def __init__(self, messenger: MessagePublisher | None = None) -> None:
        if messenger is None:
            self.messenger = MessagePublisher(consumers=[])
        else:
            self.messenger = messenger
