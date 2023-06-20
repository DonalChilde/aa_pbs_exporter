####################################################
#                                                  #
# src/snippets/pdf/extract_text_from_pdf_to_file.py
#                                                  #
####################################################
# Created by: Chad Lowe                            #
# Created on: 2022-11-10T08:32:51-07:00            #
# Last Modified: 2023-06-20T23:38:15.658195+00:00  #
# Source: https://github.com/DonalChilde/snippets  #
####################################################

# Requires pdfminer.six

import multiprocessing
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

from ..file.validate_file_out import validate_file_out


def extract_text_from_pdf_to_file(
    file_in: Path,
    file_out: Path,
    overwrite: bool = False,
    la_params: LAParams | None = None,
):
    validate_file_out(file_path=file_out, overwrite=overwrite)
    with (
        open(file_out, mode="w", encoding="utf-8") as fp_out,
        open(file_in, mode="rb") as fp_in,
    ):
        if la_params is None:
            la_params = LAParams()
        extract_text_to_fp(fp_in, fp_out, laparams=la_params)


@dataclass
class ExtractJob:
    file_in: Path
    file_out: Path
    overwrite: bool = False
    la_params: LAParams | None = None
    job_id: str = ""
    start: int | None = None
    end: int | None = None
    start_callback: Callable[["ExtractJob"], None] | None = None
    finish_callback: Callable[["ExtractJob"], None] | None = None


def do_extract_job(
    job: ExtractJob,
):
    if job.start_callback is not None:
        job.start_callback(job)
    extract_text_from_pdf_to_file(
        file_in=job.file_in,
        file_out=job.file_out,
        overwrite=job.overwrite,
        la_params=job.la_params,
    )
    if job.finish_callback is not None:
        job.finish_callback(job)


def do_extract_jobs(
    jobs: Sequence[ExtractJob],
    processes: int | None = None,
):
    with multiprocessing.Pool(processes=processes) as pool:
        pool.map(do_extract_job, jobs)
