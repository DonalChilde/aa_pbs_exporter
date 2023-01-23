from pathlib import Path

import click

from aa_pbs_exporter.snippets.click.task_complete import task_complete
from aa_pbs_exporter.snippets.pdf.extract_text_from_pdf_to_file import (
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
@click.option(
    "--name",
    "-n",
    type=Path,
    help="Specify a filename to use when exporting a single file. A .txt suffix will "
    "be added to the end of the filename.",
)
def extract(
    ctx: click.Context,
    path_in: Path,
    path_out: Path,
    overwrite: bool,
    name: Path | None,
):
    """Extract the text from one or more pdf files to new text files.

    PATH_IN can be a single pdf file, or a directory containing one or more
    pdf files. PATH_OUT must be a directory which will contain the output files. Missing
    directories will be created as needed. The default behavior is to retain the
    original file name, and change the suffix to .txt. If a different file name is
    desired, extract one file at a time, and use the --name=<filename> option.
    """
    if path_out.exists() and not path_out.is_dir():
        raise click.UsageError(
            f"PATH_OUT {path_out} is not a directory.",
            ctx=ctx,
        )
    if path_in.is_file():
        if name is None:
            extract_text_keep_name(
                file_in=path_in, dir_out=path_out, overwrite=overwrite
            )
            task_complete(ctx=ctx)
            return 0
        if name == Path(""):
            raise click.UsageError(
                f"Possible invalid file name {name}. Is it an empty string?",
                ctx=ctx,
            )

        extract_text_new_name(path_in, dir_out=path_out, name=name, overwrite=overwrite)
        task_complete(ctx=ctx)
        return 0

    if path_in.is_dir():
        pdf_files = list(path_in.glob("*.pdf"))
        click.echo(f"Found {len(pdf_files)} files.")
        if not pdf_files:
            raise click.UsageError(f"No pdf files found at {path_in}", ctx=ctx)
        for idx, pdf_file in enumerate(pdf_files):
            click.echo(f"\nExtracting {idx+1} of {len(pdf_files)} files.")
            extract_text_keep_name(
                file_in=pdf_file, dir_out=path_out, overwrite=overwrite
            )
        task_complete(ctx=ctx)
        return 0


def extract_text_new_name(
    file_in: Path, dir_out: Path, name: Path, overwrite: bool = False
):
    file_out = dir_out / append_suffix(name, ".txt")
    extract_text(file_in=file_in, file_out=file_out, overwrite=overwrite)


def extract_text_keep_name(file_in: Path, dir_out: Path, overwrite: bool = False):
    original_name = Path(file_in.name)
    new_name = append_suffix(original_name, ".txt")
    file_out = dir_out / new_name
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


def append_suffix(path: Path, suffix: str) -> Path:
    """Append a value to the last part of a path.

    Can be used to append a suffix to a filename, without removing the old suffix.
    """
    if not path.parts:
        raise ValueError(f"{path} has no parts. Was Path('') used to make it?")
    return path.parent / f"{path.parts[-1]}{suffix}"
