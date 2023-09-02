import logging
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

import click

from aa_pbs_exporter import PROJECT_SLUG
from aa_pbs_exporter.cli.extract_text_cli import extract
from aa_pbs_exporter.cli.parse import parse
from aa_pbs_exporter.snippets.file.clean_filename import clean_filename_valid
from aa_pbs_exporter.snippets.logging.logging import file_logger

# To override default settings by loading from config file, see:
# https://click.palletsprojects.com/en/8.1.x/commands/#overriding-defaults

APP_DIR = click.get_app_dir(PROJECT_SLUG)
LOG_DIR = Path(APP_DIR).expanduser() / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DATE = clean_filename_valid(datetime.now(timezone.utc).isoformat())
LOGGER_NAME = f"{PROJECT_SLUG}-{CLEAN_DATE}"
# TODO change init location so that can make customizable log level based on verbosity,
file_logger(logger_name=LOGGER_NAME, log_dir=LOG_DIR, log_level=logging.DEBUG)


@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        click.echo(f"Hello {name}!")


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.option("--verbose", "-v", count=True)
@click.pass_context
def cli(ctx: click.Context, debug: bool, verbose: int):
    """A stub with verbose and debug flag capabilities."""
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if __name__` block below)
    click.echo(f"logging at {LOG_DIR}")
    ctx.ensure_object(dict)
    ctx.obj["START_TIME"] = perf_counter_ns()
    ctx.obj["DEBUG"] = debug
    click.echo(f"Verbosity: {verbose}")
    ctx.obj["VERBOSE"] = verbose


@click.command()
@click.pass_context
def sync(ctx):
    """An example of accessing a variable passed in the context."""
    click.echo(f"Debug is {'on' if ctx.obj['DEBUG'] else 'off'}")


@click.command()
@click.pass_context
@click.argument("file_in", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("file_out", type=Path)
@click.option(
    "--overwrite",
    "-o",
    is_flag=True,
    default=False,
    show_default=True,
    help="Allow an existing file to be overwritten.",
)
def manipulate_file(ctx: click.Context, file_in: Path, file_out: Path, overwrite: bool):
    """A stub for file input and output."""
    assert isinstance(ctx, click.Context)
    assert isinstance(file_in, Path)
    assert isinstance(file_out, Path)
    # Note some check done by click on file_in, but not on file_out.
    text = file_in.read_text()
    output_text = text + "\nFile Manipulated!\n"
    # See also:
    # https://click.palletsprojects.com/en/8.1.x/options/#callbacks-for-validation
    if file_out.is_dir():
        raise click.UsageError(f"output path: {file_out} points to a directory!")
    if file_out.is_file():
        if overwrite:
            file_out.write_text(output_text)
        else:
            raise click.UsageError(
                f"output path: {file_out} exists, but overwrite is {overwrite}!"
            )
    try:
        file_out.parent.mkdir(exist_ok=True)
        file_out.write_text(output_text)
    except Exception as exc:
        raise click.UsageError(f"Error writing file at {file_out}. {exc}")


cli.add_command(extract)
cli.add_command(parse)


# if __name__ == "__main__":
#     cli(obj={})  # type: ignore
