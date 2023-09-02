from pathlib import Path

import click

from aa_pbs_exporter.snippets.click.task_complete import task_complete
from aa_pbs_exporter.snippets.pdf.extract_text_from_pdf_to_file import (
    extract_text_from_pdf_to_file,
    ExtractJob,
    do_extract_job,
    do_extract_jobs,
    extracted_text_default_file_name,
)
from time import perf_counter_ns


# TODO make snippet
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
@click.option(
    "--name",
    "-n",
    type=Path,
    help="Specify a filename to use when exporting a single file. A .txt suffix will "
    "be added to the end of the filename.",
)
@click.option(
    "--processes",
    "-p",
    type=int,
    default=4,
    show_default=True,
    help="Specify the number of processors to use when extracting multiple files. Use -1 for max.",
)
def extract(
    ctx: click.Context,
    path_in: Path,
    path_out: Path,
    overwrite: bool,
    processes: int,
    name: Path | None,
):
    """Extract the text from one or more pdf files to new text files.

    PATH_IN can be a single pdf file, or a directory containing one or more
    pdf files. PATH_OUT must be a directory which will contain the output files. Missing
    directories will be created as needed. The default behavior is to retain the
    original file name, and change the suffix to .txt. If a different file name is
    desired, extract one file at a time, and use the --name=<filename> option.
    """
    if path_out.exists() and not path_out.is_dir():
        raise click.UsageError(
            f"PATH_OUT {path_out} is not a directory.",
            ctx=ctx,
        )
    if path_in.is_file():
        if name == Path(""):
            raise click.UsageError(
                f"Possible invalid file name {name}. Is it an empty string?",
                ctx=ctx,
            )
        if name is None:
            file_out = default_name(file_in=path_in, dir_out=path_out)
        else:
            file_out = path_out / name
        job = make_job(file_in=path_in, file_out=file_out, overwrite=overwrite)
        click.echo(f"Extracting {path_in.name} to {file_out}")
        do_extract_job(job)
        task_complete(ctx=ctx)
        return 0

    if path_in.is_dir():
        pdf_files = list(path_in.glob("*.pdf"))
        click.echo(f"Found {len(pdf_files)} files.")
        click.echo(f"Extracting to {path_out}")
        if not pdf_files:
            raise click.UsageError(f"No pdf files found at {path_in}", ctx=ctx)
        jobs: list[ExtractJob] = []
        for idx, pdf_file in enumerate(pdf_files):
            file_out = default_name(pdf_file, path_out)
            job = make_job(
                file_in=pdf_file,
                file_out=file_out,
                overwrite=overwrite,
                job_id=f"{pdf_file.name} - {idx+1} of {len(pdf_files)}",
            )
            jobs.append(job)
        if processes == -1:
            proc = None
        else:
            proc = processes
        do_extract_jobs(jobs, processes=proc)
        task_complete(ctx=ctx)
        return 0


def make_job(
    file_in: Path, file_out: Path, overwrite: bool = False, job_id: str = ""
) -> ExtractJob:
    job = ExtractJob(
        file_in=file_in,
        file_out=file_out,
        overwrite=overwrite,
        job_id=job_id,
        start_callback=start_cb,
        finish_callback=finish_cb,
    )
    return job


def start_cb(job: ExtractJob):
    job.start = perf_counter_ns()


def finish_cb(job: ExtractJob):
    job.end = perf_counter_ns()
    if job.start is not None:
        length = job.end - job.start
        click.echo(f"Extracted {job.job_id} in {length/1000000000:9f} seconds.")
        return
    click.echo(f"Extracted {job.job_id}")


def default_name(file_in: Path, dir_out: Path) -> Path:
    file_out = dir_out / extracted_text_default_file_name(source=file_in)
    return file_out


def extract_text(file_in: Path, file_out: Path, overwrite: bool = False):
    click.echo(f"Extracting text from {file_in}")
    try:
        extract_text_from_pdf_to_file(
            file_in=file_in, file_out=file_out, overwrite=overwrite
        )
    except ValueError as error:
        raise click.UsageError(str(error)) from error
    click.echo(f"Wrote text to {file_out}")


def append_suffix(path: Path, suffix: str) -> Path:
    """Append a value to the last part of a path.

    Can be used to append a suffix to a filename, without removing the old suffix.
    """
    # TODO make snippet - no longer used here
    if not path.parts:
        raise ValueError(f"{path} has no parts. Was Path('') used to make it?")
    return path.parent / f"{path.parts[-1]}{suffix}"
