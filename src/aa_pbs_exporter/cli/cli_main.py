from pathlib import Path

import click

# To override default settings by loading from config file, see:
# https://click.palletsprojects.com/en/8.1.x/commands/#overriding-defaults


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
    ctx.ensure_object(dict)
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


cli.add_command(hello)
cli.add_command(sync)
cli.add_command(manipulate_file)

if __name__ == "__main__":
    cli(obj={})
