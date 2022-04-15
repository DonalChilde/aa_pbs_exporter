#!/usr/bin/env python3
"""Export all the pdf files in a directory to text files"""
import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


def extract_text_to_file(file_path_in: Path, file_path_out: Path):
    parent = file_path_out.parent
    parent.mkdir(parents=True, exist_ok=True)
    with (
        open(file_path_out, mode="w", encoding="utf-8") as file_out,
        open(file_path_in, mode="rb") as file_in,
    ):
        la_params = LAParams()
        extract_text_to_fp(file_in, file_out, laparams=la_params)


def parse_args(args: Optional[List[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, add_help=True)
    parser.add_argument(
        "source_dir",
        type=os.path.abspath,  # type: ignore
        default=None,
        nargs=1,
        help="Path to source directory.",
    )
    parser.add_argument(
        "dest_dir",
        type=os.path.abspath,  # type: ignore
        default=None,
        nargs=1,
        help="Path to destination directory.",
    )
    parsed_args = parser.parse_args(args=args)
    return parsed_args


def main(args: Optional[List[str]] = None) -> int:
    parsed_args = parse_args(args)
    source_path = Path(parsed_args.source_dir[0])
    dest_path = Path(parsed_args.dest_dir[0])
    pdf_files = source_path.glob("*.pdf")
    for file_path_in in pdf_files:
        file_out_name = Path(file_path_in.name).with_suffix(".txt")
        file_path_out = dest_path / file_out_name
        print(f"Extracting text from {file_path_in}")
        extract_text_to_file(file_path_in=file_path_in, file_path_out=file_path_out)
        print(f"Wrote text to {file_path_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
