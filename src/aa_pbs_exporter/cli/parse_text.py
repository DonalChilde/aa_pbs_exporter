from pathlib import Path

import click

from aa_pbs_exporter.pbs_2022_01.parse_pbs_txt_file import parse_pbs_txt_file
from aa_pbs_exporter.snippets.click.task_complete import task_complete


@click.command()
@click.pass_context
@click.argument("path_in", type=click.Path(exists=True, path_type=Path))
@click.argument("path_out", type=Path)
def parse(
    ctx: click.Context,
    path_in: Path,
    path_out: Path,
):
    """Parse a pairing package text file to json or yaml.

    PATH_IN can be a single txt file, or a directory containing one or more
    txt files. PATH_OUT must be a directory which will contain the output files. Missing
    directories will be created as needed.
    """
    if path_out.exists() and not path_out.is_dir():
        raise click.UsageError(
            f"PATH_OUT {path_out} is not a directory.",
            ctx=ctx,
        )
    if path_in.is_file():
        parse_pbs_txt_file(txt_file=path_in, output_dir=path_out)
        task_complete(ctx=ctx)
        return 0

    if path_in.is_dir():
        txt_files = list(path_in.glob("*.txt"))
        click.echo(f"Found {len(txt_files)} files.")
        if not txt_files:
            raise click.UsageError(f"No txt files found at {path_in}", ctx=ctx)
        for idx, txt_file in enumerate(txt_files):
            click.echo(f"\nParsing {idx+1} of {len(txt_files)} files.")
            click.echo(f"Parsing {txt_file.stem}")
            sub_dir = path_out / txt_file.stem
            parse_pbs_txt_file(txt_file=txt_file, output_dir=sub_dir)
        task_complete(ctx=ctx)
        return 0
