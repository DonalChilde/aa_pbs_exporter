import os
import shutil
from pathlib import Path

import nox

python_versions = ["3.10", "3.9", "3.8", "3.7"]
nox.needs_version = ">= 2021.6.6"
nox.options.sessions = []


@nox.session(python=python_versions[0])
def format_python(session: nox.Session):
    session.install("isort", "black")
    session.run("isort", "src", "tests")
    session.run("black", "src", "tests")


# @nox.session(python=python_versions[0])
# def tests_pycov(session: nox.Session) -> None:
#     """Run the test suite."""
#     session.install(".[testing]")

#     session.run(
#         "pytest",
#         # "--cov=src/",
#         "--cov-config=pyproject.toml",
#         "--cov-branch",
#         "--cov-report",
#         "term-missing",
#         "--cov-report",
#         "html",
#     )


@nox.session(python=python_versions[0])
def tests_cov(session: nox.Session) -> None:
    """Run the test suite."""
    session.install(".[testing]")
    session.install("coverage[toml]", "pytest", "pytest-cov", "pygments")
    try:
        session.run("coverage", "run", "--parallel", "-m", "pytest", *session.posargs)

    finally:
        if session.interactive:
            session.notify("coverage", posargs=[])


@nox.session(python=python_versions[0])
def coverage(session: nox.Session) -> None:
    """Produce the coverage report."""
    default_action = ["report"]
    args = session.posargs or default_action

    session.install("coverage[toml]")

    if not session.posargs and any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")
    if args == default_action:
        session.run("coverage", *args)
        session.run("coverage", "html")
    else:
        session.run("coverage", *args)


@nox.session(python=python_versions[0])
def safety(session: nox.Session) -> None:
    """Scan dependencies for insecure packages."""
    session.install("safety")
    session.install(".[dev,lint,doc,vscode,testing]")
    session.run("safety", "check", "--full-report")


@nox.session(name="docs-build", python=python_versions[0])
def docs_build(session: nox.Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["docs/source", "docs/build"]
    if not session.posargs and "FORCE_COLOR" in os.environ:
        args.insert(0, "--color")

    session.install(".[doc]")
    # session.install("sphinx", "sphinx-click", "furo", "myst-parser")

    build_dir = Path("docs", "build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-build", *args)


@nox.session(python=python_versions[0])
def docs(session: nox.Session) -> None:
    """Build and serve the documentation with live reloading on file changes."""
    args = session.posargs or ["--open-browser", "docs/source", "docs/build"]
    session.install(".[doc]")
    # session.install("sphinx", "sphinx-autobuild", "sphinx-click", "furo", "myst-parser")

    build_dir = Path("docs", "build")
    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)
