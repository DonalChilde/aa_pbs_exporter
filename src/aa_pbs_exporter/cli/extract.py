from logging import getLogger
from pathlib import Path

import click
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

logger = getLogger(__name__)


def extract_text_to_file(file_path_in: Path, file_path_out: Path):
    parent = file_path_out.parent
    parent.mkdir(parents=True, exist_ok=True)
    with (
        open(file_path_out, mode="w", encoding="utf-8") as file_out,
        open(file_path_in, mode="rb") as file_in,
    ):
        la_params = LAParams()
        extract_text_to_fp(file_in, file_out, laparams=la_params)


@click.group()
@click.pass_context
def extract(ctx: click.Context):
    pass


@click.command()
@click.pass_context
@click.argument("path_in", type=Path)
@click.argument("path_out", type=Path)
def pdf_to_text(ctx: click.Context, path_in: Path, path_out: Path):
    """Where is the help"""
    if path_in.is_file():
        if path_in.suffix.lower() != ".pdf":
            raise click.BadArgumentUsage(
                f"{path_in} does not end in .pdf. Is it a PDF file?"
            )
        if path_out.is_file():
            raise click.BadArgumentUsage(
                f"{path_out} is an existing file. Output path should be a directory."
            )
        file_path_out = path_out / path_in.name
        file_path_out = file_path_out.with_suffix(".txt")
        click.echo(f"Extracting {path_in} to {file_path_out}")
        extract_text_to_file(path_in, file_path_out)
        return 0
    if path_in.is_dir():
        files = path_in.glob("*.pdf")
        for file_path in files:
            file_path_out = path_out / file_path.name
            file_path_out = file_path_out.with_suffix(".txt")
            click.echo(f"Extracting {file_path} to {file_path_out}")
            extract_text_to_file(file_path, file_path_out)
        return 0
    raise click.BadArgumentUsage(
        "There was a problem with the input or output parameters."
    )


extract.add_command(pdf_to_text)
