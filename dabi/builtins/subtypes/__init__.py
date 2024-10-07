from dabi.builtins.subtypes.labels import LabelsSubtype
from dabi.builtins.subtypes.metadata import MetadataSubtype
from dabi.builtins.subtypes.selector import SelectorSubtype
from dabi.builtins.subtypes.tlb import TLBSubtype

keyword_to_subtype = {
    'tlb': TLBSubtype,
    'selector': SelectorSubtype,
    'labels': LabelsSubtype,
    'metadata': MetadataSubtype
}


def keyword_parse(keyword, item, context):
    if keyword in keyword_to_subtype:
        tmp = keyword_to_subtype[keyword](context)
        tmp.parse(item[keyword])
        return tmp
    else:
        return None
