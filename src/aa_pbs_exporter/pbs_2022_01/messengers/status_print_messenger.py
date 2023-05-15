from aa_pbs_exporter.pbs_2022_01 import messages
from aa_pbs_exporter.snippets.messages.messenger import PrintMessenger
from aa_pbs_exporter.snippets.messages.messenger_protocol import MessageProtocol


class StatusPrintMessenger(PrintMessenger):
    def _format_message(self, msg: MessageProtocol) -> str | None:
        if isinstance(msg, messages.StatusMessage):
            return msg.produce_message()
        if isinstance(msg, messages.ValidationMessage):
            return msg.produce_message()
        return None
