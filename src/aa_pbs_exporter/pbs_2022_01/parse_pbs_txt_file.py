from pathlib import Path

from aa_pbs_exporter.pbs_2022_01 import translate
from aa_pbs_exporter.pbs_2022_01.helpers.init_parse_manager import init_parse_manager
from aa_pbs_exporter.pbs_2022_01.helpers.init_publisher import init_publisher
from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_file import parse_pbs_file
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded, raw
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out


def parse_pbs_txt_file(
    txt_file: Path,
    output_dir: Path,
    compact_out: bool = True,
    expanded_out: bool = True,
) -> tuple[raw.BidPackage, compact.BidPackage | None, expanded.BidPackage | None]:
    output_dir.mkdir(parents=True, exist_ok=True)

    parse_debug = output_dir / f"{txt_file.name}-parse-debug.txt"
    translation_debug = output_dir / f"{txt_file.name}-translation-debug.txt"
    validation_debug = output_dir / f"{txt_file.name}-validation-debug.txt"
    validate_file_out(parse_debug)  # only needed once
    with (
        open(parse_debug, "w", encoding="utf-8") as parse_fp,
        open(translation_debug, "w", encoding="utf-8") as translation_fp,
        open(validation_debug, "w", encoding="utf-8") as validation_fp,
    ):
        publisher = init_publisher(
            parse_fp=parse_fp,
            translation_fp=translation_fp,
            validation_fp=validation_fp,
            std_out=True,
        )
        manager = init_parse_manager(source_path=txt_file, msg_bus=publisher)
        raw_package = parse_pbs_file(file_path=txt_file, manager=manager)
        raw_path = output_dir / raw_package.default_file_name()
        validate_file_out(raw_path)
        raw_path.write_text(raw_package.json(indent=2))
        if compact_out:
            compact_package = translate.raw_to_compact(
                raw_package=raw_package, msg_bus=publisher
            )
            compact_path = output_dir / compact_package.default_file_name()
            validate_file_out(compact_path)
            compact_path.write_text(compact_package.json(indent=2))
            if expanded_out:
                expanded_package = translate.compact_to_expanded(
                    compact_package=compact_package, msg_bus=publisher
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
