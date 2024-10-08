import yaml

from dabi.builtins import dABIContext, SmartContractType
import os

from dabi.builtins.context import load_smart_contract_template
from dabi.settings import version


class dABIParser:
    def __init__(self, root: str):
        self.context = dABIContext()
        self.context.set_root(os.path.join(root, "schema"))

    def parse(self):
        smart_contracts = []

        for subdir, dirs, files in os.walk(os.path.join(self.context.root, "contracts")):
            for file in files:
                if file.endswith('.yaml'):
                    with open(os.path.join(subdir, file), 'r') as stream:
                        data = load_smart_contract_template(root=self.context.root,
                                                            smc_yaml=stream.read())
                        smcs = list(yaml.safe_load_all(data))

                        for smc in smcs:
                            self.context.update_subcontext()
                            tmp = SmartContractType(self.context)
                            tmp.parse(smc)
                            smart_contracts.append(tmp)

        return {
            'api_version': version,
            'smart_contracts': [i.to_dict() for i in smart_contracts],
            'tlb_sources': self.context.tlb_sources
        }
