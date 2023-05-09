from io import TextIOWrapper

from aa_pbs_exporter.pbs_2022_01.messengers.debug_messenger import DebugMessenger
from aa_pbs_exporter.snippets.messages.publisher import Publisher


def init_msg_bus(debug_fp: TextIOWrapper | None = None, click_out: bool = False):
    msg_bus = Publisher(consumers=[])
    debug_messenger = DebugMessenger(file=debug_fp)
    msg_bus.consumers.append(debug_messenger)
    return msg_bus
