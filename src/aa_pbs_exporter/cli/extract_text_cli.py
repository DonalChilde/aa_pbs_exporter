from pathlib import Path

import click

from aa_pbs_exporter.util.extract_text_from_pdf_to_file import (
    extract_text_from_pdf_to_file,
)


@click.command()
@click.pass_context
@click.argument("path_in", type=click.Path(exists=True, path_type=Path))
@click.argument("path_out", type=Path)
@click.option(
    "--overwrite",
    "-o",
    is_flag=True,
    default=False,
    show_default=True,
    help="Allow an existing file to be overwritten.",
)
@click.option("--name", "-n", type=Path)
def extract(
    ctx: click.Context,
    path_in: Path,
    path_out: Path,
    overwrite: bool,
    name: Path | None,
):
    if path_in.is_file() and name is None:
        extract_text_keep_name(file_in=path_in, dir_out=path_out, overwrite=overwrite)
    if path_in.is_dir():
        pdf_files = list(path_in.glob("*.pdf"))
        if not pdf_files:
            raise click.UsageError(f"No pdf files found at {path_in}", ctx=ctx)
        for pdf_file in pdf_files:
            extract_text_keep_name(
                file_in=pdf_file, dir_out=path_out, overwrite=overwrite
            )


def extract_text_new_name(file_in: Path, file_out: Path, overwrite: bool = False):
    extract_text(file_in=file_in, file_out=file_out, overwrite=overwrite)


def extract_text_keep_name(file_in: Path, dir_out: Path, overwrite: bool = False):
    file_out_name = Path(file_in.name).with_suffix(".txt")
    file_out = dir_out / file_out_name
    extract_text(file_in=file_in, file_out=file_out, overwrite=overwrite)


def extract_text(file_in: Path, file_out: Path, overwrite: bool = False):
    click.echo(f"Extracting text from {file_in}")
    try:
        extract_text_from_pdf_to_file(
            file_in=file_in, file_out=file_out, overwrite=overwrite
        )
    except ValueError as error:
        raise click.UsageError(str(error)) from error
    click.echo(f"Wrote text to {file_out}")
