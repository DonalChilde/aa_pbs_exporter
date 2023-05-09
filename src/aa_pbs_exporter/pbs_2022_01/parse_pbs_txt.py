from pathlib import Path

from aa_pbs_exporter.pbs_2022_01 import translate
from aa_pbs_exporter.pbs_2022_01.helpers.init_msg_bus import init_msg_bus
from aa_pbs_exporter.pbs_2022_01.helpers.init_parse_manager import init_parse_manager
from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_file import parse_pbs_file
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded, raw
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out


def parse_pbs_txt_file(
    txt_file: Path,
    output_dir: Path,
    debug_path: Path,
    compact_out: bool = True,
    expanded_out: bool = True,
) -> tuple[raw.BidPackage, compact.BidPackage | None, expanded.BidPackage | None]:
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(debug_path, "w", encoding="utf-8") as debug_fp:
        msg_bus = init_msg_bus(debug_fp=debug_fp, click_out=True)
        manager = init_parse_manager(source_path=txt_file, msg_bus=msg_bus)
        raw_package = parse_pbs_file(file_path=txt_file, manager=manager)
        raw_path = output_dir / raw_package.default_file_name()
        validate_file_out(raw_path)
        raw_path.write_text(raw_package.json(indent=2))
        if compact_out:
            compact_package = translate.raw_to_compact(
                raw_package=raw_package, msg_bus=msg_bus
            )
            compact_path = output_dir / compact_package.default_file_name()
            validate_file_out(compact_path)
            compact_path.write_text(compact_package.json(indent=2))
            if expanded_out:
                expanded_package = translate.compact_to_expanded(
                    compact_package=compact_package, msg_bus=msg_bus
                )
                expanded_path = output_dir / expanded_package.default_file_name()
                validate_file_out(expanded_path)
                expanded_path.write_text(expanded_package.json(indent=2))
            else:
                expanded_package = None
        else:
            compact_package = None
            expanded_package = None
    return raw_package, compact_package, expanded_package
