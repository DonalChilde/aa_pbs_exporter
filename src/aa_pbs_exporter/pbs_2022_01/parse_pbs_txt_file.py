from pathlib import Path

from aa_pbs_exporter.pbs_2022_01.helpers.compact_pbs_file import compact_pbs_object
from aa_pbs_exporter.pbs_2022_01.helpers.expand_pbs_file import expand_pbs_object
from aa_pbs_exporter.pbs_2022_01.helpers.init_parse_manager import init_parse_manager
from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_file import parse_pbs_file
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded, raw


def parse_pbs_txt_file(
    txt_file: Path,
    output_dir: Path | None,
    debug_dir: Path | None,
    compact_out: bool = True,
    expanded_out: bool = True,
) -> tuple[raw.BidPackage, compact.BidPackage | None, expanded.BidPackage | None]:
    """A convenience function to go all the way from txt to compact to expanded with optional save to file."""
    if debug_dir is not None:
        parse_debug = debug_dir / f"{txt_file.name}-parse-debug.txt"
        compact_debug_path = debug_dir / f"{txt_file.name}-compact-debug.txt"
        expanded_debug_path = debug_dir / f"{txt_file.name}-expanded-debug.txt"
    else:
        parse_debug = None
        compact_debug_path = None
        expanded_debug_path = None
    compact_bid_package: None | compact.BidPackage = None
    expanded_bid_package: None | expanded.BidPackage = None
    manager = init_parse_manager(
        source_path=txt_file, debug_file=parse_debug, msg_bus=None
    )
    raw_bid_package = parse_pbs_file(
        file_in=txt_file,
        save_dir=output_dir,
        manager=manager,
        file_name=None,
        overwrite=False,
    )
    if compact_out:
        compact_bid_package = compact_pbs_object(
            save_dir=output_dir,
            file_name=None,
            overwrite=False,
            debug_file=compact_debug_path,
            raw_bid_package=raw_bid_package,
        )
        if expanded_out:
            expanded_bid_package = expand_pbs_object(
                save_dir=output_dir,
                file_name=None,
                overwrite=False,
                debug_file=expanded_debug_path,
                compact_bid_package=compact_bid_package,
            )

    return (raw_bid_package, compact_bid_package, expanded_bid_package)
