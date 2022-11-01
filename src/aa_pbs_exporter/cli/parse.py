# from logging import getLogger
# from pathlib import Path

# import click
# from aa_pbs_exporter.pilot_pbs_2022.parser_2 import (
#     parse_file,
#     save_package_to_json,
#     sensible_file_name,
# )

# logger = getLogger(__name__)


# @click.command()
# @click.pass_context
# @click.argument("path_in", type=Path)
# @click.argument("path_out", type=Path)
# @click.option(
#     "split", "-s", type=click.BOOL, help="split the bid packages by base and equipment."
# )
# @click.option("year", "-y", type=int, default=2022)
# def parse_txt(
#     ctx: click.Context, path_in: Path, path_out: Path, year: int, split: bool
# ):
#     if path_in.is_file():
#         if path_in.suffix.lower() != ".txt":
#             raise click.BadArgumentUsage(
#                 f"{path_in} does not end in .txt. Is it the correct file?"
#             )
#         if path_out.is_file():
#             raise click.BadArgumentUsage(
#                 f"{path_out} is an existing file. Output path should be a directory."
#             )

#         click.echo(f"Parsing {path_in}")
#         package = parse_file(path_in, year)
#         file_path_out = path_out / sensible_file_name(package)  # FIXME
#         file_path_out = file_path_out.with_suffix(".json")
#         save_package_to_json(file_path_out, package)
#         click.echo(f"Saved {path_in} to {file_path_out}")
#         return 0
#     if path_in.is_dir():
#         click.echo(f"Parsing files from {path_in} to {path_out}")
#         files = path_in.glob("*.txt")
#         for file in files:
#             click.echo(f"Parsing {file}")
#             package = parse_file(file, year)
#             file_path_out = path_out / sensible_file_name(package)  # FIXME
#             file_path_out = file_path_out.with_suffix(".json")
#             save_package_to_json(file_path_out, package)
#             click.echo(f"Saved {file} to {file_path_out}")
#         return 0
#     raise click.BadArgumentUsage(
#         "There was a problem with the input or output parameters."
#     )
