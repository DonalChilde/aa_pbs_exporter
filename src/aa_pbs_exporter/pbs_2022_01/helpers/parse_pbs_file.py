import logging
import multiprocessing
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from aa_pbs_exporter.pbs_2022_01.helpers.parse_pbs_strings import parse_pbs_strings
from aa_pbs_exporter.pbs_2022_01.models.raw import BidPackage, save_raw
from aa_pbs_exporter.pbs_2022_01.parser.parse_manager import ParseManager
from aa_pbs_exporter.snippets.timers import timers

logger = logging.getLogger(__name__)
time_logger = timers.TimeLogger(logger=logger, level=logging.INFO)


@timers.timer_ns(time_logger)
def parse_pbs_file(
    file_in: Path,
    save_dir: Path | None,
    manager: ParseManager[BidPackage],
    file_name: str | None = None,
    overwrite: bool = False,
) -> BidPackage:
    with open(file_in, encoding="utf-8") as txt_file:
        data = parse_pbs_strings(strings=txt_file, manager=manager)
    assert data is not None
    if save_dir is not None:
        save_raw(
            save_dir=save_dir,
            file_name=file_name,
            overwrite=overwrite,
            bid_package=data,
        )
    return data


# @function_timer(logger=logger, level=logging.INFO)
# def parse_text_file_to_pbs_package(
#     file_in: Path,
#     file_out: Path | None,
#     overwrite: bool,
#     manager: ParseManager[BidPackage],
# ) -> BidPackage:
#     # TODO remove this function, as it is now combined with above.
#     bid_package = parse_pbs_file(file_in=file_in, manager=manager)
#     if file_out is not None:
#         save_raw(file_out=file_out, overwrite=overwrite, bid_package=bid_package)
#     return bid_package


@dataclass
class ParseJob:
    file_in: Path
    save_dir: Path | None
    file_name: str | None
    overwrite: bool
    manager: ParseManager[BidPackage]
    job_id: str = ""
    start: int | None = None
    end: int | None = None
    start_callback: Callable[["ParseJob"], None] | None = None
    finish_callback: Callable[["ParseJob"], None] | None = None


def do_parse_job(
    job: ParseJob,
):
    if job.start_callback is not None:
        job.start_callback(job)
    parse_pbs_file(
        file_in=job.file_in,
        save_dir=job.save_dir,
        file_name=job.file_name,
        overwrite=job.overwrite,
        manager=job.manager,
    )
    if job.finish_callback is not None:
        job.finish_callback(job)


def do_parse_jobs(
    jobs: Sequence[ParseJob],
    processes: int | None = None,
):
    with multiprocessing.Pool(processes=processes) as pool:
        pool.map(do_parse_job, jobs)
