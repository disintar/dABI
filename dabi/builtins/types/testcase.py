import json
import os
import warnings
from datetime import datetime

from tonpy import MASTER_SHARD, LiteClient, BlockIdExt, BlockId, TVM, C7, Address, StackEntry, add_tlb

from dabi.builtins.types.base import dABIType
from dabi.settings import supported_versions

from time import sleep


class TCaseType(dABIType):
    smart_contract = {
        'workchain': -1,
        'shard': MASTER_SHARD,
        'seqno': None
    }

    address = None

    def __init__(self, context, abi):
        super().__init__(context)

        self.client = self.load_client()
        self.parsed_info = {}
        self.abi = abi
        self.name = None
        self.libs = []
        self.only_storage = False

        self.block_cache = dict()

    def load_client(self):
        server = json.loads(os.getenv('LITESERVER'))

        return LiteClient(host=server['ip'],
                          port=server['port'],
                          pubkey_base64=server['id']['key'],
                          timeout=5,
                          num_try=100)

    def process_tlb(self, expected, received: StackEntry, expected_item, my_error):
        received_tlb = {}

        my_item = self.abi['tlb_sources'][expected_item['tlb']['id']]['tlb']
        if expected_item['tlb']['use_block_tlb']:
            my_item = f"{my_item}\n\n{self.abi['tlb_sources']['block_tlb']}"
        add_tlb(my_item, received_tlb)

        to_parse = received_tlb[expected_item['tlb']['object']]()

        if received.get_type() is StackEntry.Type.t_cell:
            data = to_parse.cell_unpack(received.get())
        elif received.get_type() is StackEntry.Type.t_slice:
            data = to_parse.unpack(received.get(), True)
        else:
            item = received.get().end_cell()
            data = to_parse.cell_unpack(item, True)
        parsed_data = data.dump(with_types=expected_item['tlb']['dump_with_types'])
        assert expected == parsed_data, f"{my_error}, parsed: {parsed_data}"

    def check_result_rec(self, test_item, received: StackEntry, expected_item, error_holder=None):
        t = received.get_type()
        my_error = f"({expected_item['labels']}) {error_holder}, getter expected: {test_item}, received {received.get()}"

        if expected_item['labels'].get('skipParse', False):
            return

        if expected_item['type'] == 'Tuple':
            if t is not StackEntry.Type.t_tuple:
                raise AssertionError(my_error)

            for expected_inner, stack_item in zip(expected_item['items'], received.get()):
                self.check_result_rec(test_item, stack_item, expected_inner, error_holder)
            return

        if expected_item['labels']['name'] not in test_item and not expected_item.get("required", False):
            raise ValueError(
                f"{error_holder}, ABI type of getter has no test for label: {expected_item['labels']['name']}")

        if expected_item.get("required", False):
            expected = expected_item.get("required", False)
        else:
            expected = test_item[expected_item['labels']['name']]

        is_address = False
        if 'address' in expected_item['labels'] and expected_item['labels']['address'] is True:
            is_address = True
            expected = Address(expected)

        is_string = False
        if 'string' in expected_item['labels'] and expected_item['labels']['string'] is True:
            is_string = True

        if t is StackEntry.Type.t_null:
            if not is_address:
                assert expected is None or not len(expected), my_error
            else:
                assert expected == Address(), f"{my_error}, addr_none"
        elif t is StackEntry.Type.t_cell:
            if not is_address:
                if not is_string:
                    if 'tlb' in expected_item:
                        self.process_tlb(expected, received, expected_item, my_error)
                    else:
                        assert expected == received.get().get_hash(), f"{my_error}, {received.get().get_hash()}"
                else:
                    received = received.get().begin_parse().load_string()
                    assert expected == received, f"{my_error}, {received}"
            else:
                received = received.get().begin_parse().load_address()
                assert expected == received, f"{my_error}, {received}"
        elif t is StackEntry.Type.t_slice:
            if not is_address:
                if not is_string:
                    if 'tlb' in expected_item:
                        self.process_tlb(expected, received, expected_item, my_error)
                    else:
                        assert expected == received.get().get_hash(), f"{my_error}, {received.get().get_hash()}"
                else:
                    received = received.get().load_string()
                    assert expected == received, f"{my_error}, {received}"
            else:
                received = received.get().load_address()
                assert expected == received, f"{my_error}, {received}"
        elif t is StackEntry.Type.t_int:

            if expected_item['type'] == 'Bool':
                received = received.get() == -1
            else:
                received = received.get()

            if not is_address:
                assert expected == received, f"{my_error}"
            else:
                received = hex(received)[2:].upper().zfill(64)
                assert expected.address == received, f"{my_error}, {Address(f"{0}:{received}")}"

        elif t is StackEntry.Type.t_builder:
            if not is_address:
                if not is_string:
                    if 'tlb' in expected_item:
                        self.process_tlb(expected, received, expected_item, my_error)
                    else:
                        assert expected == received.get().get_hash(), f"{my_error}"
                else:
                    received = received.get().end_cell().begin_parse().load_string()
                    assert expected == received, f"{my_error}, {received}"
            else:
                received = received.get().end_cell().begin_parse().load_address()
                assert expected == received, f"{my_error}, {received}"
        elif t is StackEntry.Type.t_vmcont:
            assert expected == received.get().get_hash(), my_error
        else:
            raise ValueError(f"{error_holder}, Not supported type in getter: {t}")

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

        if 'libs' in data['smart_contract']:
            if isinstance(data['smart_contract']['libs'], list):
                self.libs = data['smart_contract']['libs']
            else:
                raise ValueError('TestCaseType: libs must be a list')
        try:
            self.address = Address(data['smart_contract']['address'])
        except Exception as e:
            raise ValueError(f'TestCaseType: address is invalid: {e}')

        if 'parsed_info' not in data or not isinstance(data['parsed_info'], dict):
            raise ValueError('TestCaseType: parsed_info must be a dict')

        has_getters = 'get_methods' in data['parsed_info'] and isinstance(data['parsed_info']['get_methods'], dict)
        has_storage = 'storage' in data['parsed_info'] and isinstance(data['parsed_info']['storage'], dict)

        if not has_getters and not has_storage:
            raise ValueError('TestCaseType: parsed_info must contain get_methods or storage')

        if has_getters:
            for getter in data['parsed_info']['get_methods']:
                if not isinstance(data['parsed_info']['get_methods'][getter], dict):
                    raise ValueError(f'TestCaseType: {getter} is not a dict')

                if getter not in self.parsed_info:
                    self.parsed_info[getter] = {}

                    if 'result' not in data['parsed_info']['get_methods'][getter]:
                        raise ValueError(f'TestCaseType: does not contain result for {getter}')

                    if not isinstance(data['parsed_info']['get_methods'][getter]['result'], list):
                        if data['parsed_info']['get_methods'][getter]['result'] is None:
                            data['parsed_info']['get_methods'][getter]['result'] = []
                        else:
                            raise ValueError(f'TestCaseType: {getter} must contain a list of results')

                    for i in data['parsed_info']['get_methods'][getter]['result']:
                        if len(i) < 1:
                            raise ValueError(
                                f'TestCaseType: {getter} must contain at least one result in list of results')
                        if not isinstance(i, dict):
                            raise ValueError(f'TestCaseType: {getter} / {i} must be dict')

                        for j in i:
                            self.parsed_info[getter][j] = i[j]

        if has_storage:
            # Record storage expectations; may be storage-only test
            self.parsed_info['__storage__'] = data['parsed_info']['storage']
            self.only_storage = not has_getters

    def get_tvm(self):

        bid = BlockId(
            workchain=self.smart_contract['workchain'],
            shard=self.smart_contract['shard'],
            seqno=self.smart_contract['seqno']
        )

        if bid not in self.block_cache:
            not_loaded = True
            while not_loaded:

                try:
                    self.block_cache[bid] = self.client.lookup_block(workchain=bid.workchain, shard=bid.shard,
                                                                     seqno=bid.seqno).blk_id
                    not_loaded = False
                except Exception as e:
                    sleep(0.1)

                    # raise ValueError(f'TestCaseType: block {bid} not found: {e}')

        block = self.block_cache[bid]

        account_state = self.client.get_account_state(self.address, block).get_parsed()
        t = 0

        while account_state is None:
            self.client = self.load_client()

            print(f"Loading account state for {self.address}...")
            sleep(0.1)
            t += 1
            if t > 20:
                raise ValueError(f'TestCaseType: account state not found after 10 tries: {self.address}')

            account_state = self.client.get_account_state(self.address, block).get_parsed()

        code = account_state.storage.state.x.code.value
        data = account_state.storage.state.x.data.value

        tvm = TVM(data=data, code=code, allow_debug=True)
        tvm.set_gas_limit(5000000, 5000000)

        if len(self.libs):
            libs_data = self.client.get_libraries(self.libs)
            tvm.set_libs(libs_data)

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

        # Storage validation: if storage is requested in parsed_info, verify storage values against TLB-parsed data
        if '__storage__' in self.parsed_info:
            if 'storage' not in contract:
                raise ValueError(f"Test Case: {self.name} has no storage in interface")
            storage = contract['storage']
            tlb_id = storage.get('id')
            if not tlb_id or tlb_id not in self.abi['tlb_sources']:
                raise ValueError(f"Test Case: storage TLB id not registered for {self.name}")

            # Prepare TLB parser for storage
            tlb_text = self.abi['tlb_sources'][tlb_id]['tlb']
            if storage.get('use_block_tlb', False):
                tlb_text = f"{tlb_text}\n\n{self.abi['tlb_sources']['block_tlb']}"
            parsed_tlb = {}
            add_tlb(tlb_text, parsed_tlb)
            to_parse = parsed_tlb[storage['object']]()

            # Load current account data cell
            bid = BlockId(
                workchain=self.smart_contract['workchain'],
                shard=self.smart_contract['shard'],
                seqno=self.smart_contract['seqno']
            )
            if bid not in self.block_cache:
                not_loaded = True
                while not_loaded:
                    try:
                        self.block_cache[bid] = self.client.lookup_block(workchain=bid.workchain, shard=bid.shard,
                                                                         seqno=bid.seqno).blk_id
                        not_loaded = False
                    except Exception:
                        sleep(0.1)

            block = self.block_cache[bid]
            account_state = self.client.get_account_state(self.address, block).get_parsed()
            data_cell = account_state.storage.state.x.data.value

            # Parse data cell and dump to dict
            parsed_obj = to_parse.cell_unpack(data_cell)
            dump = parsed_obj.dump(with_types=storage.get('dump_with_types', False))

            # Helper to traverse dump by dotted path
            def _get_by_path(root, path_str):
                cur = root
                for part in path_str.split('.'):
                    if isinstance(cur, dict) and part in cur:
                        cur = cur[part]
                    else:
                        raise AssertionError(f"Test Case: {self.name} storage path not found: {path_str}, dump: {root}")
                return cur

            expected_map = self.parsed_info['__storage__']
            parse_items = {item.get('path'): item for item in storage.get('parse', [])} if storage.get('parse') else {}

            # Compare only provided expected keys; skip paths with skipParse label
            for key, expected_value in expected_map.items():
                labels = parse_items.get(key, {}).get('labels', {}) if parse_items else {}
                if labels.get('skipParse', False):
                    continue
                actual_value = _get_by_path(dump, key)
                assert expected_value == actual_value, \
                    f"Test Case: {self.name} storage mismatch at '{key}': expected {expected_value}, got {actual_value}"

            # If this test is storage-only, do not proceed with getters
            if self.only_storage:
                return

        for getter in contract['get_methods']:
            for instance in contract['get_methods'][getter]:

                method_name = instance['method_name']
                if method_name not in self.parsed_info:
                    labels = instance.get('labels', {})
                    if labels is None:
                        labels = {}

                    if 'skipLive' in labels and labels['skipLive']:
                        continue

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
                        instance[
                            'method_result']), f"{error_holder}, method result length is not equal to ABI one, stack: {stack.unpack_rec()}, got: {len(stack)}, expected: {len(instance['method_result'])}"

                if instance['result_strict_type_check']:
                    my_result_hash = stack.get_abi_hash()
                    assert my_result_hash == instance[
                        'method_result_hash'], f"{error_holder}, method result hash is not equal to ABI one, stack: {stack.unpack_rec()}"

                for stack_item, expected_item in zip(stack, instance['method_result']):
                    if expected_item['labels'].get('skipParse', False):
                        continue

                    exp = expected_item['type']

                    if expected_item['type'] == 'Int' and 'dton_type' not in expected_item[
                        'labels'] and 'required' not in expected_item:
                        raise Exception(
                            f'!!!!!!!!!!!! dton_type not found for {expected_item["labels"]["name"]} field, method {method_name}')

                    if exp == 'Bool':
                        exp = 'Int'

                    if not stack_item.as_abi()['type'] == exp and expected_item['labels'].get('address', False):
                        self.check_result_rec(current_test, stack_item, expected_item, error_holder)
                    else:
                        assert stack_item.as_abi()[
                                   'type'] == exp, f"{error_holder}, ABI type of getter is not equal to {expected_item['type']}"

                        self.check_result_rec(current_test, stack_item, expected_item, error_holder)
