from datetime import datetime
from pathlib import Path

import click

from aa_pbs_exporter.models.bid_package_2022_10.bid_package import BidPackage
from aa_pbs_exporter.models.bid_package_2022_10.translate_2022_10 import (
    translate_package,
)
from aa_pbs_exporter.models.raw_2022_10.validate import validate_bid_package
from aa_pbs_exporter.parsers.parser_2022_10.line_parser import (
    LineParseContext,
    parse_file,
)
from aa_pbs_exporter.snippets.parsing.parse_context import DevParseContext
from aa_pbs_exporter.snippets.click.task_complete import task_complete
from aa_pbs_exporter.snippets.file.validate_file_out import validate_file_out
from aa_pbs_exporter.snippets.click.click_message_consumer import (
    ClickMessageConsumer,
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
# @click.option(
#     "--name",
#     "-n",
#     type=Path,
#     help="Specify a filename to use when parsing a single file. A .json, .yaml, "
#     "and/or .txt suffix will be added to the end of the filename.",
# )
@click.option(
    "--split-package",
    "-s",
    is_flag=True,
    default=False,
    show_default=True,
    help="Split package based on base and equipment.",
)
@click.option(
    "--json-output",
    "-j",
    is_flag=True,
    default=False,
    show_default=True,
    help="Save json output.",
)
@click.option(
    "--yaml-output",
    "-y",
    is_flag=True,
    default=False,
    show_default=True,
    help="Save yaml output.",
)
@click.option(
    "--debug-output",
    "-d",
    is_flag=True,
    default=False,
    show_default=True,
    help="Save debug output.",
)
def parse(
    ctx: click.Context,
    path_in: Path,
    path_out: Path,
    overwrite: bool,
    # name: Path | None,
    debug_output: bool,
    json_output: bool,
    yaml_output: bool,
    split_package: bool,
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
        parse_ctx = LineParseContext(
            source_name=str(path_in), message_consumers=[ClickMessageConsumer()]
        )
        parse_source_file(
            file_in=path_in,
            ctx=parse_ctx,
            dir_out=path_out,
            debug_out=debug_output,
            json_out=json_output,
            yaml_out=yaml_output,
            overwrite=overwrite,
        )
        task_complete(ctx=ctx)
        return 0

    if path_in.is_dir():
        txt_files = list(path_in.glob("*.txt"))
        click.echo(f"Found {len(txt_files)} files.")
        if not txt_files:
            raise click.UsageError(f"No txt files found at {path_in}", ctx=ctx)
        for idx, txt_file in enumerate(txt_files):
            click.echo(f"\nParsing {idx+1} of {len(txt_files)} files.")
            parse_ctx = LineParseContext(
                source_name=str(txt_file), message_consumers=[ClickMessageConsumer()]
            )
            parse_source_file(
                file_in=txt_file,
                ctx=parse_ctx,
                dir_out=path_out,
                debug_out=debug_output,
                json_out=json_output,
                yaml_out=yaml_output,
                overwrite=overwrite,
            )
        task_complete(ctx=ctx)
        return 0


def parse_source_file(
    file_in: Path,
    ctx: LineParseContext,
    dir_out: Path,
    debug_out: bool,
    json_out: bool,
    yaml_out: bool,
    overwrite: bool = False,
) -> BidPackage:
    if debug_out:
        debug_file_out = debug_file_path(file_in, dir_out=dir_out)
        validate_file_out(file_path=debug_file_out, overwrite=overwrite)
        with open(debug_file_out, mode="w", encoding="utf-8") as fp_out:
            dev_ctx = DevParseContext(
                source_name=ctx.source_name, wrapped_context=ctx, fp_out=fp_out
            )
            raw_package = parse_file(file_path=file_in, ctx=dev_ctx)  # type: ignore
    else:
        raw_package = parse_file(file_path=file_in, ctx=ctx)
    validate_bid_package(bid_package=raw_package, ctx=ctx)
    bid_package = translate_package(bid_package=raw_package, source=raw_package.source)
    if json_out:
        file_out = json_file_path(bid_package=bid_package, dir_out=dir_out)
        save_package_json(file_out, bid_package=bid_package, overwrite=overwrite)
    if yaml_out:
        file_out = yaml_file_path(bid_package, dir_out=dir_out)
        save_package_yaml(file_path=file_out, bid_package=bid_package)
    return bid_package


def debug_file_path(source_file: Path, dir_out: Path) -> Path:
    return dir_out / f"{source_file.name}_DEBUG.txt"


def file_name_from_date(value: datetime) -> str:
    date_str = value.strftime("%Y_%m_%d")
    return date_str


def json_file_path(bid_package: BidPackage, dir_out: Path) -> Path:
    bases = [bid_package.base]
    bases.extend(bid_package.satelite_bases)
    # equipment = bid_package.
    file_name = f"{file_name_from_date(bid_package.from_date)}_{'_'.join(bases)}.json"
    return dir_out / file_name


def yaml_file_path(bid_package: BidPackage, dir_out: Path) -> Path:
    raise NotImplementedError


def save_package_json(file_path: Path, bid_package: BidPackage, overwrite: bool):
    validate_file_out(file_path=file_path, overwrite=overwrite)
    file_path.write_text(bid_package.json(indent=2))


def save_package_yaml(file_path: Path, bid_package: BidPackage):
    raise NotImplementedError


def output_stats(file_path: Path, bid_package: BidPackage):
    raise NotImplementedError
