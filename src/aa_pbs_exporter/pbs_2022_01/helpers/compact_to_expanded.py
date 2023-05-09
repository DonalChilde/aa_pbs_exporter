from aa_pbs_exporter.pbs_2022_01 import translate, validate
from aa_pbs_exporter.pbs_2022_01.models import compact
from aa_pbs_exporter.snippets.messages.publisher import Publisher


def compact_to_expanded(compact_package: compact.BidPackage, msg_bus: Publisher):
    validator = validate.ExpandedValidator(msg_bus=msg_bus)
    translator = translate.CompactToExpanded(validator=validator)
    expanded_package = translator.translate(compact_package)
    return expanded_package
