import logging
import multiprocessing
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from aa_pbs_exporter.pbs_2022_01 import translate
from aa_pbs_exporter.pbs_2022_01.models import compact, raw
from aa_pbs_exporter.snippets.timers.function_timer import function_timer

logger = logging.getLogger(__name__)


@function_timer(logger=logger, level=logging.INFO)
def compact_pbs_file(
    file_in: Path,
    save_dir: Path | None,
    file_name: str | None,
    overwrite: bool,
    debug_file: Path | None,
) -> compact.BidPackage:
    raw_bid_package = raw.load_raw(file_in=file_in)
    return compact_pbs_object(
        raw_bid_package=raw_bid_package,
        save_dir=save_dir,
        file_name=file_name,
        overwrite=overwrite,
        debug_file=debug_file,
    )


@function_timer(logger=logger, level=logging.INFO)
def compact_pbs_object(
    save_dir: Path | None,
    file_name: str | None,
    overwrite: bool,
    debug_file: Path | None,
    raw_bid_package: raw.BidPackage,
) -> compact.BidPackage:
    compact_bid_package = translate.raw_to_compact(
        raw_package=raw_bid_package, debug_file=debug_file
    )
    if save_dir is not None:
        compact.save_compact(
            save_dir=save_dir,
            file_name=file_name,
            overwrite=overwrite,
            bid_package=compact_bid_package,
        )
    return compact_bid_package


@dataclass
class CompactJob:
    file_in: Path
    save_dir: Path
    file_name: str | None
    debug_file: Path | None
    overwrite: bool
    job_id: str = ""
    start: int | None = None
    end: int | None = None
    start_callback: Callable[["CompactJob"], None] | None = None
    finish_callback: Callable[["CompactJob"], None] | None = None


def do_compact_job(job: CompactJob):
    if job.start_callback is not None:
        job.start_callback(job)
    compact_pbs_file(
        file_in=job.file_in,
        save_dir=job.save_dir,
        file_name=job.file_name,
        overwrite=job.overwrite,
        debug_file=job.debug_file,
    )
    if job.finish_callback is not None:
        job.finish_callback(job)


def do_compact_jobs(
    jobs: Sequence[CompactJob],
    processes: int | None = None,
):
    with multiprocessing.Pool(processes=processes) as pool:
        pool.map(do_compact_job, jobs)
