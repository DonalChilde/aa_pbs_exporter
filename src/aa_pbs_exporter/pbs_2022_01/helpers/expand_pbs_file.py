import logging
import multiprocessing
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from aa_pbs_exporter.pbs_2022_01 import translate
from aa_pbs_exporter.pbs_2022_01.models import compact, expanded
from aa_pbs_exporter.snippets.timers import timers

logger = logging.getLogger(__name__)

time_logger = timers.TimeLogger(logger=logger, level=logging.INFO)


@timers.timer_ns(time_logger)
def expand_pbs_file(
    file_in: Path,
    save_dir: Path | None,
    file_name: str | None,
    overwrite: bool,
    debug_file: Path | None,
) -> expanded.BidPackage:
    compact_bid_package = compact.load_compact(file_in=file_in)
    return expand_pbs_object(
        save_dir=save_dir,
        file_name=file_name,
        overwrite=overwrite,
        debug_file=debug_file,
        compact_bid_package=compact_bid_package,
    )


@timers.timer_ns(time_logger)
def expand_pbs_object(
    save_dir: Path | None,
    file_name: str | None,
    overwrite: bool,
    debug_file: Path | None,
    compact_bid_package: compact.BidPackage,
) -> expanded.BidPackage:
    expanded_bid_package = translate.translate_compact_to_expanded(
        compact_package=compact_bid_package, debug_file=debug_file
    )
    if save_dir is not None:
        expanded.save_expanded(
            save_dir=save_dir,
            file_name=file_name,
            overwrite=overwrite,
            bid_package=expanded_bid_package,
        )
    return expanded_bid_package


@dataclass
class ExpandJob:
    file_in: Path
    save_dir: Path
    file_name: str | None
    debug_file: Path | None
    overwrite: bool
    job_id: str = ""
    start: int | None = None
    end: int | None = None
    start_callback: Callable[["ExpandJob"], None] | None = None
    finish_callback: Callable[["ExpandJob"], None] | None = None


def do_expand_job(job: ExpandJob):
    if job.start_callback is not None:
        job.start_callback(job)
    expand_pbs_file(
        file_in=job.file_in,
        save_dir=job.save_dir,
        file_name=job.file_name,
        overwrite=job.overwrite,
        debug_file=job.debug_file,
    )
    if job.finish_callback is not None:
        job.finish_callback(job)


def do_expand_jobs(
    jobs: Sequence[ExpandJob],
    processes: int | None = None,
):
    with multiprocessing.Pool(processes=processes) as pool:
        pool.map(do_expand_job, jobs)
