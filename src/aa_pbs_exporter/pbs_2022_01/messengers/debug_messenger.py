from aa_pbs_exporter.pbs_2022_01 import messages
from aa_pbs_exporter.snippets.messages.messenger import PrintMessenger
from aa_pbs_exporter.snippets.messages.messenger_protocol import MessageProtocol


class DebugMessenger(PrintMessenger):
    def _format_message(self, msg: MessageProtocol) -> str:
        return super()._format_message(msg)
