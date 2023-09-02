# from pathlib import Path

# import click

# from aa_pbs_exporter.pbs_2022_01.api import parse_pbs_txt_file
# from aa_pbs_exporter.snippets.click.task_complete import task_complete
# from aa_pbs_exporter.snippets.indexed_string.state_parser.parse_exception import (
#     ParseException,
# )

# # TODO make this parse only, use translate for next steps.


# @click.command()
# @click.pass_context
# @click.argument("path_in", type=click.Path(exists=True, path_type=Path))
# @click.argument("path_out", type=Path)
# @click.option("--debug-path", "-d", type=Path, default=None)
# @click.option("--debug/--no-debug", default=True, show_default=True)
# @click.option("--compact/--no-compact", default=True, show_default=True)
# @click.option("--expand/--no-expand", default=True, show_default=True)
# def parse(
#     ctx: click.Context,
#     path_in: Path,
#     path_out: Path,
#     debug: bool,
#     debug_path: Path | None,
#     compact: bool,
#     expand: bool,
# ) -> int:
#     """Parse a pairing package text file to json or yaml.

#     PATH_IN can be a single txt file, or a directory containing one or more
#     txt files. PATH_OUT must be a directory which will contain the output files. Missing
#     directories will be created as needed.
#     """
#     if path_out.exists() and not path_out.is_dir():
#         raise click.UsageError(
#             f"PATH_OUT {path_out} is not a directory.",
#             ctx=ctx,
#         )
#     if path_in.is_file():
#         # parse_pbs_txt_file(txt_file=path_in, output_dir=path_out)
#         parse_the_file(path_out=path_out, txt_file=path_in)
#         task_complete(ctx=ctx)
#         return 0

#     if path_in.is_dir():
#         txt_files = list(path_in.glob("*.txt"))
#         click.echo(f"Checking {path_in} for files.")
#         click.echo(f"Found {len(txt_files)} files.")
#         if not txt_files:
#             raise click.UsageError(f"No txt files found at {path_in}", ctx=ctx)
#         for idx, txt_file in enumerate(txt_files):
#             click.echo(f"\nParsing {idx+1} of {len(txt_files)} files.")
#             parse_the_file(path_out=path_out, txt_file=txt_file)
#             # click.echo(f"Parsing {txt_file.stem}")
#             # sub_dir = path_out / txt_file.stem
#             # try:
#             #     parse_pbs_txt_file(txt_file=txt_file, output_dir=sub_dir)
#             # except ParseException as error:
#             #     click.echo(f"There was an error parsing {txt_file}")
#             #     click.echo("Check the logs for more details.")
#             #     click.echo(error)
#         task_complete(ctx=ctx)
#         return 0
#     raise click.UsageError("There was an unexpected error.")


# def parse_the_file(path_out: Path, txt_file: Path):
#     sub_dir = path_out / txt_file.name.split(".")[0]
#     click.echo(f"Parsing {txt_file} to {sub_dir}")
#     try:
#         parse_pbs_txt_file(txt_file=txt_file, output_dir=sub_dir, debug_dir=sub_dir)
#     except ParseException as error:
#         click.echo(f"There was an error parsing {txt_file}")
#         click.echo("Check the logs for more details.")
#         click.echo(error)
