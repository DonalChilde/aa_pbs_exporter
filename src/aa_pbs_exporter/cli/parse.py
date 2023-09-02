import multiprocessing
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import click

from aa_pbs_exporter.pbs_2022_01 import api
from aa_pbs_exporter.snippets.click.task_complete import task_complete
from aa_pbs_exporter.snippets.indexed_string.typedict.state_parser.parse_exception import (
    ParseException,
)


@click.command()
@click.pass_context
@click.argument("path-in", type=click.Path(exists=True, path_type=Path))
@click.argument(
    "path-out",
    type=click.Path(
        exists=False, file_okay=False, dir_okay=True, writable=True, path_type=Path
    ),
)
@click.option(
    "-p",
    "--processes",
    type=int,
    default=1,
    show_default=True,
    help="The number of processes to use.",
)
@click.option(
    "-o",
    "--overwrite/--no-overwrite",
    default=False,
    show_default=True,
    help="Enable overwrite of output files.",
)
def parse(
    ctx: click.Context,
    path_in: Path,
    path_out: Path,
    processes: int,
    # parents_included: int,
    overwrite: bool,
):
    """Parse a PBS txt file.

    PATH-IN - A file or directory containing a PBS txt file. If a directory, all files ending in '.txt' will be parsed.

    PATH-OUT - The destination directory. Will be created if it doesn't exist. Parsed files will be placed here.

    """
    if path_in.is_file():
        parse_args = config_parse_args(
            base_path=path_in.parent,
            file_in=path_in,
            path_out=path_out,
            overwrite=overwrite,
        )
        do_parse_args(parse_args=parse_args)
    if path_in.is_dir():
        files = collect_input_files(path_in=path_in)
        jobs = collect_parse_args(
            base_path=path_in, input_files=files, path_out=path_out, overwrite=overwrite
        )
        click.echo(f"Found {len(jobs)} files to parse.")
        do_parse_jobs(jobs=jobs, processes=processes)

    task_complete(ctx=ctx)
    return 0


@dataclass
class ParseArgs:
    file_in: Path
    file_out: Path
    debug_out: Path
    overwrite: bool


def do_parse_args(parse_args: ParseArgs):
    parse_one_file(
        file_in=parse_args.file_in,
        file_out=parse_args.file_out,
        debug_out=parse_args.debug_out,
        overwrite=parse_args.overwrite,
    )


def parse_one_file(file_in: Path, file_out: Path, debug_out: Path, overwrite: bool):
    # check for overwrite before doing parse work.
    if not overwrite and file_out.exists():
        raise click.BadOptionUsage(
            "overwrite",
            message=f"Destination {file_out} exists, and overwrite was not enabled.",
        )
    try:
        results = api.parse_pbs_txt_file(
            file_in=file_in, debug_file=debug_out, job_name=file_in.stem, metadata={}
        )
        api.save_parse_results(
            file_out=file_out, parse_results=results, overwrite=overwrite
        )
        click.echo(f"Parsed {file_in}")
    except ParseException as exc:
        click.echo(f"There was an error parsing {file_in}. \n\t{exc}")


def collect_input_files(path_in: Path) -> list[Path]:
    files = path_in.rglob("*.txt")
    return list(files)


def collect_parse_args(
    base_path: Path,
    input_files: Iterable[Path],
    path_out: Path,
    # parents_included: int,
    overwrite: bool,
) -> list[ParseArgs]:
    parse_args_list: list[ParseArgs] = []
    assert base_path.is_dir()
    for input_file in input_files:
        parse_args_list.append(
            config_parse_args(
                base_path=base_path,
                file_in=input_file,
                path_out=path_out,
                # parents_included=parents_included,
                overwrite=overwrite,
            )
        )
    return parse_args_list


def config_parse_args(
    base_path: Path,
    file_in: Path,
    path_out: Path,
    overwrite: bool,
) -> ParseArgs:
    output_path = expand_output_path(
        base_path=base_path, file_in=file_in, path_out=path_out
    )
    file_name = parsed_file_name(file_in=file_in)
    file_out = output_path / file_name
    debug_out = output_path / debug_file_name(file_in=file_in)
    parse_args = ParseArgs(
        file_in=file_in, file_out=file_out, debug_out=debug_out, overwrite=overwrite
    )
    return parse_args


def expand_output_path(base_path: Path, file_in: Path, path_out: Path) -> Path:
    if base_path == file_in:
        return path_out
    rel_path = file_in.parent.absolute().relative_to(base_path.absolute())
    # fragment = parents_fragment(file_in=file_in, parents_included=parents_included)
    return path_out / rel_path


def parents_fragment(file_in: Path, parents_included: int) -> Path:
    """Return a fragment of the parent path.

    Args:
        file_in - the path to be evaluated.
        parents_included - How many levels of parent to return.
            Negative numbers slice from the end of the path.

    """
    # TODO make snippet, fix docstring.
    if len(file_in.parents) < parents_included:
        raise ValueError(
            f"{file_in.parents!r} is shorter than the desired path fragment length of {parents_included}"
        )
    if parents_included == 0:
        return Path()
    parents_sliced = file_in.parents[parents_included:]
    return Path(*parents_sliced)


def parsed_file_name(file_in: Path) -> Path:
    file_name = Path(f"{file_in.stem}-parsed.json")
    return file_name


def debug_file_name(file_in: Path) -> Path:
    file_name = Path(f"{file_in.stem}-debug.txt")
    return file_name


def do_parse_jobs(
    jobs: Sequence[ParseArgs],
    processes: int | None = None,
):
    with multiprocessing.Pool(processes=processes) as pool:
        pool.map(do_parse_args, jobs)
