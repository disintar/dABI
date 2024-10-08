from pprint import pprint

from dabi.builtins.context import load_smart_contract_template
from test_base import *


def test_get_method():
    with open('tests/examples/smc.yaml', 'r') as stream:
        data = load_smart_contract_template(root=context.root, smc_yaml=stream.read())
        smcs = list(yaml.safe_load_all(data))
        context.update_subcontext()

        tmp = SmartContractType(context)
        smc = smcs[0]
        tmp.parse(smc)

        assert tmp.to_dict() == {'get_methods': [{'labels': None,
                                                  'metadata': {'description': '', 'link': '', 'name': ''},
                                                  'method_args': [],
                                                  'method_args_hash': '080FB7C908744FDC42C99B777511A890B04242167D30CD0F3EC4A3A542E1EB79',
                                                  'method_id': 85793,
                                                  'method_name': 'get_cool_smc',
                                                  'method_result': [{'labels': {'name': 'anon_0'},
                                                                     'metadata': {'description': '',
                                                                                  'link': '',
                                                                                  'name': ''},
                                                                     'required': 256,
                                                                     'type': 'Int'}],
                                                  'method_result_hash': 'E6EB6425907C5A933F7A883A368950B0AE6094BF897660145D6A4210817FE743',
                                                  'result_length_strict_check': True,
                                                  'result_strict_type_check': True},
                                                 {'labels': {},
                                                  'metadata': {'description': '', 'link': '', 'name': ''},
                                                  'method_args': [{'labels': {'name': 'anon_1'},
                                                                   'metadata': {'description': '',
                                                                                'link': '',
                                                                                'name': ''},
                                                                   'required': None,
                                                                   'type': 'Cell'},
                                                                  {'labels': {'name': 'test'},
                                                                   'metadata': {'description': '',
                                                                                'link': '',
                                                                                'name': ''},
                                                                   'required': None,
                                                                   'type': 'Slice'},
                                                                  {'items': [{'labels': {'name': 'anon_3'},
                                                                              'metadata': {'description': '',
                                                                                           'link': '',
                                                                                           'name': ''},
                                                                              'required': None,
                                                                              'type': 'Int'}],
                                                                   'labels': {'name': 'anon_2'},
                                                                   'metadata': {'description': '',
                                                                                'link': '',
                                                                                'name': ''},
                                                                   'required': None,
                                                                   'type': 'Tuple'}],
                                                  'method_args_hash': '1D11BE84A6C9FC477169F2E7E7D734C17CC6A096CAC6F34971D367D1E5209098',
                                                  'method_id': 123631,
                                                  'method_name': 't1',
                                                  'method_result': [],
                                                  'method_result_hash': 'AE2A55DD8FC509FB84F03E978C7DE250D74C8A7E95E8FC52C23C6CC155690347',
                                                  'result_length_strict_check': True,
                                                  'result_strict_type_check': True}],
                                 'labels': {'dton_parse_prefix': 'parsed_smart_', 'name': 'my_unique_smc'},
                                 'metadata': {'description': 'Completely not useless',
                                              'link': '',
                                              'name': 'My cool smart contract'},
                                 'selector': {'items': [], 'selector_type': 'by_methods'}}
