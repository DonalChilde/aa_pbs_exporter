from hashlib import md5
from pathlib import Path

from aa_pbs_exporter.pbs_2022_01 import translate, validate
from aa_pbs_exporter.pbs_2022_01.models.common import HashedFile
from aa_pbs_exporter.pbs_2022_01.models.raw import BidPackage
from aa_pbs_exporter.pbs_2022_01.parser.parse_manager import ParseManager
from aa_pbs_exporter.pbs_2022_01.parser.result_handlers.raw_parse_handler import (
    RawResultHandler,
)
from aa_pbs_exporter.snippets import messages
from aa_pbs_exporter.snippets.hash.file_hash import make_hashed_file


def init_parse_manager(
    source_path: Path | None = None,
    msg_bus: messages.MessagePublisher | None = None,
) -> ParseManager[BidPackage]:
    if source_path is None:
        source = source_path
    else:
        source = make_hashed_file(
            file_path=source_path, hasher=md5(), result_factory=HashedFile.factory
        )
    validator = validate.RawValidator(msg_bus=msg_bus)
    translator = translate.ParsedToRaw(
        source=source, validator=validator, msg_bus=msg_bus
    )
    result_handler: RawResultHandler = RawResultHandler(
        translator=translator, msg_bus=msg_bus
    )
    manager: ParseManager[BidPackage] = ParseManager(result_handler=result_handler)
    return manager
