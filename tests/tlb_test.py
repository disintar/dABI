from tests.test_base import *


def test_tlb():
    with open('../tests/examples/tlb.yaml', 'r') as stream:
        tlbs = list(yaml.safe_load_all(stream))
        context.update_subcontext()

        tlb_obj = TLBSubtype(context)
        tlb_obj.parse(tlbs[0]['tlb'])
        assert tlb_obj.to_dict()['object'] == 'AWithTwoBits'
        context.update_subcontext()

        tlb_obj = TLBSubtype(context)
        tlb_obj.parse(tlbs[1]['tlb'])
        assert tlb_obj.to_dict()['object'] == 'CoolMessage'
