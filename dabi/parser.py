from collections import defaultdict

import yaml
import json

from dabi.builtins import dABIContext, InterfaceType
import os

from dabi.builtins.context import load_smart_contract_template
from dabi.settings import version

current_file_path = os.path.dirname(os.path.abspath(__file__))


class dABIParser:
    def __init__(self, root: str):
        self.context = dABIContext()
        self.context.set_root(os.path.join(root, "schema"))

        with open(os.path.join(current_file_path, "method_to_hash.json")) as f:
            self.method_to_hash = json.load(f)

    def parse(self):
        interfaces = []

        for subdir, dirs, files in os.walk(os.path.join(self.context.root, "interfaces")):
            for file in files:
                if file.endswith('.yaml'):
                    with open(os.path.join(subdir, file), 'r') as stream:
                        data = load_smart_contract_template(root=self.context.root,
                                                            smc_yaml=stream.read())
                        smcs = list(yaml.safe_load_all(data))

                        for smc in smcs:
                            self.context.update_subcontext()
                            tmp = InterfaceType(self.context)
                            tmp.parse(smc)
                            interfaces.append(tmp)

        by_name = {}
        by_get_method = {}
        by_code_hash = {}
        by_get_method_stats = {}

        for i in interfaces:
            parsed_i = i.to_dict(convert_getters=True)
            name_of_i = parsed_i['labels']['name']

            if name_of_i in by_name:
                raise ValueError(f"Interface name duplicated: {name_of_i}")

            by_name[name_of_i] = parsed_i

            for method in parsed_i['get_methods']:
                if method not in by_get_method:
                    by_get_method[method] = []

                by_get_method[method].append(name_of_i)

                if str(method) in self.method_to_hash:
                    stat = 0

                    for code_hash in self.method_to_hash[str(method)]:
                        stat += 1
                        if code_hash not in by_code_hash:
                            by_code_hash[code_hash] = []

                        by_code_hash[code_hash].append(name_of_i)

                    by_get_method_stats[method] = stat

            for code_hash in parsed_i['code_hashes']:
                if code_hash not in by_code_hash:
                    by_code_hash[code_hash] = []

                by_code_hash[code_hash].append(name_of_i)

        return {
            'api_version': version,
            'by_name': by_name,
            'by_get_method': by_get_method,
            'by_code_hash': by_code_hash,
            'by_get_method_stats': by_get_method_stats,
            'tlb_sources': self.context.tlb_sources
        }
