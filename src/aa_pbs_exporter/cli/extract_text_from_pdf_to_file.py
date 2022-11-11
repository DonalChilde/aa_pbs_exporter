from pathlib import Path
from typing import List, Optional

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


def extract_text_from_pdf_to_file(
    file_path_in: Path, file_path_out: Path, la_params: LAParams | None = None
):
    parent = file_path_out.parent
    parent.mkdir(parents=True, exist_ok=True)
    with (
        open(file_path_out, mode="w", encoding="utf-8") as file_out,
        open(file_path_in, mode="rb") as file_in,
    ):
        if la_params is None:
            la_params = LAParams()
        extract_text_to_fp(file_in, file_out, laparams=la_params)
