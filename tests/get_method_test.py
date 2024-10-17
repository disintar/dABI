from pprint import pprint

from tests.test_base import *


def test_get_method():
    with open('tests/examples/get_methods.yaml', 'r') as stream:
        methods = list(yaml.safe_load_all(stream))
        context.update_subcontext()

        tmp = InterfaceType(context)
        get_method = GetMethodType(context, anon_getter=tmp.anon_getter)
        get_method.parse(methods[0])
        assert get_method.to_dict() == [
            {'metadata': {'name': '', 'description': '', 'link': ''}, 'labels': {}, 'method_name': 't1',
             'method_id': 123631, 'method_args': [
                {'type': 'Cell', 'metadata': {'name': '', 'description': '', 'link': ''}, 'labels': {'name': 'anon_0'},
                 'required': None},
                {'type': 'Slice', 'metadata': {'name': '', 'description': '', 'link': ''}, 'labels': {'name': 'test'},
                 'required': None},
                {'type': 'Tuple', 'metadata': {'name': '', 'description': '', 'link': ''}, 'labels': {'name': 'anon_1'},
                 'required': None, 'items': [{'type': 'Int', 'metadata': {'name': '', 'description': '', 'link': ''},
                                              'labels': {'name': 'anon_2'}, 'required': None}]}], 'method_result': [],
             'method_args_hash': '98BC78F7A0C43451AEBB9021F9AF162EAAB8091FE58D2B2E4BE15975362D5DFA',
             'method_result_hash': 'DFCFC220CB3D6DC8D2FA97A226B4612B5F57C9E6D265FC8C71E55D54C4F12758',
             'result_strict_type_check': True, 'result_length_strict_check': True}]

        context.update_subcontext()

        tmp = InterfaceType(context)
        get_method = GetMethodType(context, anon_getter=tmp.anon_getter)
        get_method.parse(methods[1])

        assert get_method.to_dict() == [{'metadata': {'name': 'my-cool-get-method',
                                                      'description': 'Get my cool data from this methods', 'link': ''},
                                         'labels': {'dton_parse_prefix': 'parsed_cool_'}, 'method_name': 'get_cool_smc',
                                         'method_id': 85793, 'method_args': [
                {'type': 'Cell', 'metadata': {'name': 'Test cell', 'description': '', 'link': ''},
                 'labels': {'name': 'anon_0'}, 'required': None},
                {'type': 'Slice', 'metadata': {'name': '', 'description': '', 'link': ''}, 'labels': {'name': 'anon_1'},
                 'required': None,
                 'tlb': {'id': '546DDE1FA200A9995CDD473F0D2E31BB85ECDC1A9EF2809BAD5DBB4EA70F390A', 'object': 'TestB',
                         'use_block_tlb': True, 'dump_with_types': False}},
                {'type': 'Tuple', 'metadata': {'name': '', 'description': '', 'link': ''}, 'labels': {'name': 'anon_2'},
                 'required': None, 'items': [{'type': 'Cell', 'metadata': {'name': '', 'description': '', 'link': ''},
                                              'labels': {'name': 'anon_3'}, 'required': None},
                                             {'type': 'Slice', 'metadata': {'name': '', 'description': '', 'link': ''},
                                              'labels': {'name': 'anon_4'}, 'required': None, 'tlb': {
                                                 'id': '546DDE1FA200A9995CDD473F0D2E31BB85ECDC1A9EF2809BAD5DBB4EA70F390A',
                                                 'object': 'TestC', 'use_block_tlb': True, 'dump_with_types': False}},
                                             {'type': 'Tuple', 'metadata': {'name': '', 'description': '', 'link': ''},
                                              'labels': {'name': 'anon_5'}, 'required': None, 'items': [{'type': 'Int',
                                                                                                         'metadata': {
                                                                                                             'name': '',
                                                                                                             'description': '',
                                                                                                             'link': ''},
                                                                                                         'labels': {
                                                                                                             'name': 'anon_6'},
                                                                                                         'required': None}]}]}],
                                         'method_result': [
                                             {'type': 'Int', 'metadata': {'name': '', 'description': '', 'link': ''},
                                              'labels': {'name': 'anon_7'}, 'required': 256}, {'type': 'Cell',
                                                                                               'metadata': {
                                                                                                   'name': 'Content of my NFT',
                                                                                                   'description': '',
                                                                                                   'link': ''},
                                                                                               'labels': {
                                                                                                   'field': 'content',
                                                                                                   'name': 'anon_8'},
                                                                                               'required': None}],
                                         'method_args_hash': '72DAF4E4501AA52B4FB31D19008738B4221A932DA6889F802DEBD58717C584E5',
                                         'method_result_hash': '99235F69B11F79CE0E16F8C9A06DCB7D954EFB24557EABBCB6209572C0CA6FF8',
                                         'result_strict_type_check': True, 'result_length_strict_check': False}, {
                                            'metadata': {'name': 'my-cool-get-method',
                                                         'description': 'Get my cool data from this methods',
                                                         'link': ''}, 'labels': {'dton_parse_prefix': 'parsed_cool_'},
                                            'method_name': 'second_method', 'method_id': 87882, 'method_args': [],
                                            'method_result': [
                                                {'type': 'Int', 'metadata': {'name': '', 'description': '', 'link': ''},
                                                 'labels': {'name': 'anon_9'}, 'required': None}],
                                            'method_args_hash': 'DFCFC220CB3D6DC8D2FA97A226B4612B5F57C9E6D265FC8C71E55D54C4F12758',
                                            'method_result_hash': '3032DE3E7074799554B1C159F288DC80674452119D5AF0074E70B3F7A3A2C1C9',
                                            'result_strict_type_check': True, 'result_length_strict_check': True}, {
                                            'metadata': {'name': 'my-cool-get-method',
                                                         'description': 'Get my cool data from this methods',
                                                         'link': 'https://lol.me/'},
                                            'labels': {'dton_parse_prefix': 'parsed_cool_', 'sub_field': 'ok'},
                                            'method_name': 'test', 'method_id': 105222, 'method_args': [],
                                            'method_result': [
                                                {'type': 'Int', 'metadata': {'name': '', 'description': '', 'link': ''},
                                                 'labels': {'field': 'test_int', 'name': 'anon_10'}, 'required': None}],
                                            'method_args_hash': 'DFCFC220CB3D6DC8D2FA97A226B4612B5F57C9E6D265FC8C71E55D54C4F12758',
                                            'method_result_hash': '3032DE3E7074799554B1C159F288DC80674452119D5AF0074E70B3F7A3A2C1C9',
                                            'result_strict_type_check': True, 'result_length_strict_check': True}]
