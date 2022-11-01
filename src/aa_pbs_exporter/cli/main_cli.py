# """Console script entry point for aa_pbs_exporter."""


# from logging import getLogger

# import click

# from .cli_app import App
# from .extract import pdf_to_text
# from .parse import parse_txt

# logger = getLogger(__name__)


# @click.group()
# @click.option("-v", "--verbose", count=True)
# @click.pass_context
# def main(ctx: click.Context, verbose):
#     """Console script for aa_pbs_exporter."""
#     init_ctx_obj(ctx, verbose)
#     # TODO make an About message
#     click.echo("AA PBS Package Exporter")


# def init_ctx_obj(context: click.Context, verbose):
#     """Init the context.obj custom object."""
#     context.obj = App({}, verbose)
#     context.obj.config = {"key": "oh so important"}


# main.add_command(pdf_to_text)
# main.add_command(parse_txt)
