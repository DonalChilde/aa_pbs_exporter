from pathlib import Path

from aa_pbs_exporter.pbs_2022_01.models import compact, expanded, raw
from aa_pbs_exporter.pbs_2022_01.parse_pbs_txt_file import parse_pbs_txt_file
from aa_pbs_exporter.snippets.pdf.extract_text_from_pdf_to_file import (
    extract_text_from_pdf_to_file,
)


def parse_pbs_pdf_file(
    pdf_file: Path,
    output_dir: Path,
    compact_out: bool = True,
    expanded_out: bool = True,
) -> tuple[raw.BidPackage, compact.BidPackage | None, expanded.BidPackage | None]:
    output_path = output_dir / pdf_file.name
    output_path = output_path.with_suffix(".txt")
    extract_text_from_pdf_to_file(file_in=pdf_file, file_out=output_path)
    return parse_pbs_txt_file(
        txt_file=output_path,
        output_dir=output_dir,
        compact_out=compact_out,
        expanded_out=expanded_out,
    )
