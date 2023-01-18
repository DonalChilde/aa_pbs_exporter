####################################################
#                                                  #
#      src/snippets/click/task_complete.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-13T12:22:09-07:00            #
# Last Modified: 2022-12-03T23:45:37.160003+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################
from time import perf_counter_ns

import click


def task_complete(ctx: click.Context):
    """Assuming the ctx.obj is a dict with START_TIME defined, output a task completed message."""
    start_time = ctx.obj.get("START_TIME", None)
    if start_time is not None:
        end_time = perf_counter_ns()
        length = end_time - start_time
        click.echo(f"\nTask completed in {length/1000000000:9f} seconds.")
