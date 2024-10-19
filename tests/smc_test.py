from pprint import pprint

from dabi.builtins.context import load_smart_contract_template
from tests.test_base import *


def test_get_method():
    with open('tests/examples/smc.yaml', 'r') as stream:
        data = load_smart_contract_template(root=context.root, smc_yaml=stream.read())
        print(data.getvalue())
        smcs = list(yaml.safe_load_all(data))
        context.update_subcontext()

        tmp = InterfaceType(context)
        smc = smcs[0]
        tmp.parse(smc)

        assert tmp.to_dict() == {
            'metadata': {'name': 'My cool smart contract', 'description': 'Completely not useless', 'link': ''},
            'labels': {'dton_parse_prefix': 'parsed_smart_', 'name': 'my_unique_smc'},
            'selector': {'selector_type': 'by_methods', 'items': []}, 'get_methods': {85793: [
                {'metadata': {'name': '', 'description': '', 'link': ''}, 'labels': {}, 'method_name': 'get_cool_smc',
                 'method_id': 85793, 'method_args': [], 'method_result': [
                    {'type': 'Int', 'metadata': {'name': '', 'description': '', 'link': ''},
                     'labels': {'name': 'anon_0'}, 'required': 256}],
                 'method_args_hash': 'DFCFC220CB3D6DC8D2FA97A226B4612B5F57C9E6D265FC8C71E55D54C4F12758',
                 'method_result_hash': '3032DE3E7074799554B1C159F288DC80674452119D5AF0074E70B3F7A3A2C1C9',
                 'result_strict_type_check': True, 'result_length_strict_check': True}], 123631: [
                {'metadata': {'name': '', 'description': '', 'link': ''}, 'labels': {}, 'method_name': 't1',
                 'method_id': 123631, 'method_args': [
                    {'type': 'Cell', 'metadata': {'name': '', 'description': '', 'link': ''},
                     'labels': {'name': 'anon_1'}, 'required': None},
                    {'type': 'Slice', 'metadata': {'name': '', 'description': '', 'link': ''},
                     'labels': {'name': 'test'}, 'required': None},
                    {'type': 'Tuple', 'metadata': {'name': '', 'description': '', 'link': ''},
                     'labels': {'name': 'anon_2'}, 'required': None, 'items': [
                        {'type': 'Int', 'metadata': {'name': '', 'description': '', 'link': ''},
                         'labels': {'name': 'anon_3'}, 'required': None}]}], 'method_result': [],
                 'method_args_hash': '98BC78F7A0C43451AEBB9021F9AF162EAAB8091FE58D2B2E4BE15975362D5DFA',
                 'method_result_hash': 'DFCFC220CB3D6DC8D2FA97A226B4612B5F57C9E6D265FC8C71E55D54C4F12758',
                 'result_strict_type_check': True, 'result_length_strict_check': True}]}, 'code_hashes': []}
