import importlib
import logging
from typing import List

from tests.aa_pbs_exporter.conftest import PackageResource

from aa_pbs_exporter.pbs_2022_01.models import raw
from aa_pbs_exporter.pbs_2022_01 import parse as line_parser
from aa_pbs_exporter.snippets.parsing.state_parser import parse_file

SENTINEL = False


def test_phx(pairing_text_files: List[PackageResource], logger: logging.Logger):
    if not SENTINEL:
        return
    ctx = parse_city("PHX", pairing_text_files, logger)
    assert len(ctx.bid_package.pages) > 10


def test_mia(pairing_text_files: List[PackageResource], logger: logging.Logger):
    if not SENTINEL:
        return
    ctx = parse_city("MIA", pairing_text_files, logger)
    assert len(ctx.bid_package.pages) > 10


def test_lax(pairing_text_files: List[PackageResource], logger: logging.Logger):
    if not SENTINEL:
        return
    ctx = parse_city("LAX", pairing_text_files, logger)
    assert len(ctx.bid_package.pages) > 10


def test_bos(pairing_text_files: List[PackageResource], logger: logging.Logger):
    if not SENTINEL:
        return
    ctx = parse_city("BOS", pairing_text_files, logger)
    assert len(ctx.bid_package.pages) > 10


def test_dfw(pairing_text_files: List[PackageResource], logger: logging.Logger):
    if not SENTINEL:
        return
    ctx = parse_city("DFW", pairing_text_files, logger)
    assert len(ctx.bid_package.pages) > 10


def test_clt(pairing_text_files: List[PackageResource], logger: logging.Logger):
    if not SENTINEL:
        return
    ctx = parse_city("CLT", pairing_text_files, logger)
    assert len(ctx.bid_package.pages) > 10


def test_dca(pairing_text_files: List[PackageResource], logger: logging.Logger):
    if not SENTINEL:
        return
    ctx = parse_city("DCA", pairing_text_files, logger)
    assert len(ctx.bid_package.pages) > 10


def test_lga(pairing_text_files: List[PackageResource], logger: logging.Logger):
    if not SENTINEL:
        return
    ctx = parse_city("LGA", pairing_text_files, logger)
    assert len(ctx.bid_package.pages) > 10


def test_ord(pairing_text_files: List[PackageResource], logger: logging.Logger):
    if not SENTINEL:
        return
    ctx = parse_city("ORD", pairing_text_files, logger)
    assert len(ctx.bid_package.pages) > 10


def test_phl(pairing_text_files: List[PackageResource], logger: logging.Logger):
    if not SENTINEL:
        return
    ctx = parse_city("PHL", pairing_text_files, logger)
    assert len(ctx.bid_package.pages) > 10


def parse_city(
    city: str, pairing_text_files: List[PackageResource], logger
) -> line_parser.LineParseContext:
    scheme = line_parser.ParseScheme()
    for resource in [x for x in pairing_text_files if city in x.name]:
        with importlib.resources.path(resource.package, resource.name) as file_path:
            logger.info("Parsing %s.%s", resource.package, resource.name)
            ctx = line_parser.LineParseContext(str(file_path))
            parse_file(
                file_path, scheme=scheme, ctx=ctx, skipper=line_parser.make_skipper()
            )
            return ctx


# def test_all_full_packages(
#     pairing_text_files: List[PackageResource], logger: logging.Logger
# ):
#     scheme = parser.ParseScheme()
#     for resource in pairing_text_files:
#         with importlib.resources.path(resource.package, resource.name) as file_path:
#             logger.info("Parsing %s.%s", resource.package, resource.name)
#             ctx = parser.ParseContext(str(file_path))
#             parse_file(file_path, scheme=scheme, ctx=ctx, skipper=parser.make_skipper())
#             assert len(ctx.bid_package.pages) > 10
