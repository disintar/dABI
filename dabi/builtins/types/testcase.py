import json
import os
import warnings
from datetime import datetime

from tonpy import MASTER_SHARD, LiteClient, BlockIdExt, BlockId, TVM, C7, Address, StackEntry

from dabi.builtins.types.base import dABIType
from dabi.settings import supported_versions


def check_result_rec(test_item, received: StackEntry, expected_item, error_holder=None):
    t = received.get_type()
    my_error = f"{error_holder}, getter expected: {test_item}, received {received}"

    if expected_item['type'] == 'Tuple':
        if t is not StackEntry.Type.t_tuple:
            raise AssertionError(my_error)

        for expected_inner, stack_item in zip(expected_item['items'], t.get()):
            check_result_rec(test_item, stack_item, expected_inner, error_holder)
        return

    if expected_item['labels']['name'] not in test_item:
        raise ValueError(
            f"{error_holder}, ABI type of getter has no test for label: {expected_item['labels']['name']}")

    expected = test_item[expected_item['labels']['name']]

    is_address = False
    if 'address' in expected_item['labels'] and expected_item['labels']['address'] is True:
        is_address = True
        expected = Address(expected)

    if t is StackEntry.Type.t_null:
        assert expected is None or not len(expected), my_error
    elif t is StackEntry.Type.t_cell:
        if not is_address:
            assert expected == received.get().get_hash(), my_error
        else:
            received = received.get().begin_parse().load_address()
            assert expected == received, f"{my_error}, {received}"
    elif t is StackEntry.Type.t_slice:
        if not is_address:
            assert expected == received.get().get_hash(), my_error
        else:
            received = received.get().load_address()
            assert expected == received, f"{my_error}, {received}"
    elif t is StackEntry.Type.t_int:
        assert expected == received.get(), my_error
    elif t is StackEntry.Type.t_builder:
        if not is_address:
            assert expected == received.get().get_hash(), my_error
        else:
            received = received.get().end_cell().begin_parse().load_address()
            assert expected == received, f"{my_error}, {received}"
    elif t is StackEntry.Type.t_vmcont:
        assert expected == received.get().get_hash(), my_error
    else:
        raise ValueError(f"{error_holder}, Not supported type in getter: {t}")


class TCaseType(dABIType):
    smart_contract = {
        'workchain': -1,
        'shard': MASTER_SHARD,
        'seqno': None
    }

    address = None

    def __init__(self, context, abi):
        super().__init__(context)

        server = json.loads(os.getenv('LITESERVER'))
        self.client = LiteClient(host=server['ip'],
                                 port=server['port'],
                                 pubkey_base64=server['id']['key'],
                                 timeout=5)
        self.parsed_info = {}
        self.abi = abi
        self.name = None

    def parse(self, data):
        if not isinstance(data, dict):
            raise ValueError('TestCaseType: data must be a dict')

        if 'apiVersion' not in data or not isinstance(data['apiVersion'], str) or data[
            'apiVersion'] not in supported_versions:
            raise ValueError('TestCaseType: apiVersion must be one of {}'.format(supported_versions))

        if 'smart_contract' not in data or not isinstance(data['smart_contract'], dict):
            raise ValueError('TestCaseType: smart_contract must be dict type')

        if 'address' not in data['smart_contract'] or not isinstance(data['smart_contract']['address'], str):
            raise ValueError('TestCaseType: address must be in smart_contract and must be string')

        if 'block' not in data['smart_contract'] or not isinstance(data['smart_contract']['block'], dict):
            raise ValueError('TestCaseType: block must be in smart_contract and must be dictionary')

        if 'mc_seqno' not in data['smart_contract']['block']:
            raise ValueError('TestCaseType: mc_seqno must be in block')

        if not isinstance(data['smart_contract']['block']['mc_seqno'], int):
            raise ValueError('TestCaseType: mc_seqno must be int')

        self.smart_contract['seqno'] = data['smart_contract']['block']['mc_seqno']

        if 'name' not in data['smart_contract'] or not isinstance(data['smart_contract']['name'], str):
            raise ValueError('TestCaseType: name must be in smart_contract (name of label.smart_contract to test)')
        self.name = data['smart_contract']['name']

        try:
            self.address = Address(data['smart_contract']['address'])
        except Exception as e:
            raise ValueError(f'TestCaseType: address is invalid: {e}')

        if 'parsed_info' not in data or not isinstance(data['parsed_info'], dict) or not 'get_methods' in data[
            'parsed_info']:
            raise ValueError('TestCaseType: parsed_info must contain get_methods as dict')

        for getter in data['parsed_info']['get_methods']:
            if not isinstance(data['parsed_info']['get_methods'][getter], dict):
                raise ValueError(f'TestCaseType: {getter} is not a dict')

            if getter not in self.parsed_info:
                self.parsed_info[getter] = {}

                if 'result' not in data['parsed_info']['get_methods'][getter]:
                    raise ValueError(f'TestCaseType: does not contain result for {getter}')

                if not isinstance(data['parsed_info']['get_methods'][getter]['result'], list):
                    raise ValueError(f'TestCaseType: {getter} must contain a list of results')

                for i in data['parsed_info']['get_methods'][getter]['result']:
                    if len(i) < 1:
                        raise ValueError(f'TestCaseType: {getter} must contain at least one result in list of results')
                    if not isinstance(i, dict):
                        raise ValueError(f'TestCaseType: {getter} / {i} must be dict')

                    for j in i:
                        self.parsed_info[getter][j] = i[j]

    def get_tvm(self):
        block = self.client.lookup_block(block=BlockId(
            workchain=self.smart_contract['workchain'],
            shard=self.smart_contract['shard'],
            seqno=self.smart_contract['seqno']
        )).blk_id

        account_state = self.client.get_account_state(self.address, block).get_parsed()

        code = account_state.storage.state.x.code.value
        data = account_state.storage.state.x.data.value

        tvm = TVM(data=data, code=code, allow_debug=True)
        tvm.set_gas_limit(5000000, 5000000)

        config = self.client.get_config_all(block)

        c7 = C7(
            time=datetime.now(),
            balance_grams=account_state.storage.balance.grams.amount.value,
            address=self.address,
            my_code=code,
            global_config=config[1].get_cell()
        )
        tvm.set_c7(c7)

        return tvm

    def validate(self):
        if self.name not in self.abi['by_name']:
            raise ValueError(f"Test Case: Smart contract {self.name} not found")

        contract = self.abi['by_name'][self.name]

        for getter in contract['get_methods']:
            for instance in contract['get_methods'][getter]:

                method_name = instance['method_name']
                if method_name not in self.parsed_info:
                    warnings.warn(
                        f'TestCaseType: {method_name} of {self.name} does not contain expected result in tests')
                    continue
                current_test = self.parsed_info[method_name]

                error_holder = f"Test Case: {self.name} test faild on {instance['method_name']} method"
                tvm = self.get_tvm()

                args = []
                if 'args' in instance:
                    raise NotImplementedError

                tvm.set_stack([*args, getter])

                stack = tvm.run(allow_non_success=True, unpack_stack=False)

                if tvm.exit_code not in [0, 1]:
                    raise ValueError(f"{error_holder}, TVM {tvm.exit_code} failed")

                if instance['result_length_strict_check']:
                    assert len(stack) == len(
                        instance['method_result']), f"{error_holder}, method result length is not equal to ABI one"

                if instance['result_strict_type_check']:
                    my_result_hash = stack.get_abi_hash()
                    assert my_result_hash == instance[
                        'method_result_hash'], f"{error_holder}, method result hash is not equal to ABI one"

                for stack_item, expected_item in zip(stack, instance['method_result']):
                    assert stack_item.as_abi()['type'] == expected_item[
                        'type'], f"{error_holder}, ABI type of getter is not equal to {expected_item['type']}"

                    check_result_rec(current_test, stack_item, expected_item, error_holder)
