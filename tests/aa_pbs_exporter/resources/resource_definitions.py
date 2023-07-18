from tests.aa_pbs_exporter.resources.helpers_3 import ResourceLocator


PARSED_1 = ResourceLocator(
    "tests.aa_pbs_exporter.pbs_2022_01.parse.resources.page",
    "ThreePages_three_pages.json",
)
"""A short, multipage CollectedParseResults."""

COLLECTED_1 = ResourceLocator(
    "tests.aa_pbs_exporter.pbs_2022_01.translate.resources.collected",
    "ThreePages_three_pages-collected.json",
)
"""A three page raw bid package."""

COMPACT_1 = ResourceLocator(
    "tests.aa_pbs_exporter.pbs_2022_01.translate.resources.compact",
    "ThreePages_three_pages-collected-compact.json",
)
"""A three page compact bid package."""
