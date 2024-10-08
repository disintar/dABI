from dabi.builtins.subtypes.metadata import MetadataSubtype
from dabi.builtins.subtypes.labels import LabelsSubtype
from dabi.builtins.subtypes.selector import SelectorSubtype
from dabi.builtins.types.get_methods import MethodsSubtype
from dabi.builtins.types.base import dABIType
import re

from dabi.settings import supported_versions


class SmartContractType(dABIType):
    def __init__(self, context):
        super().__init__(context)

        self.metadata = MetadataSubtype(context)
        self.labels = LabelsSubtype(context)
        self.selector = SelectorSubtype(context)
        self.get_methods = []
        self.unique_getters = set()
        self.current_unique_index = 0

    def anon_getter(self, name):
        if name is None:
            cur_name = f"anon_{self.current_unique_index}"
            self.current_unique_index += 1
            if cur_name not in self.unique_getters:
                self.unique_getters.add(cur_name)
                return cur_name
            else:
                raise ValueError(f'MethodsSubtype: Method name {cur_name} already exists')
        else:
            if name in self.unique_getters:
                raise ValueError(f'MethodsSubtype: Method name {name} already exists')
            self.unique_getters.add(name)
            return name

    def parse(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError('SmartContractType: data must be dict')

        assert data['apiVersion'] in supported_versions, "SmartContractType API version must be supported"

        if 'metadata' in data:
            self.metadata.parse(data['metadata'])

        if 'labels' in data:
            self.labels.parse(data['labels'])

        if self.labels.data is None or 'name' not in self.labels.data or not isinstance(self.labels.data['name'], str):
            raise ValueError('SmartContractType: labels must have "name" field unique for each SMC')

        pattern = r'^[A-Za-z_][A-Za-z0-9_]*$'
        if re.match(pattern, self.labels.data['name']) is None:
            raise ValueError("SmartContractType: name must match pattern '{}'".format(pattern))

        self.context.register_smc(self.labels.data['name'])

        if 'spec' not in data:
            raise ValueError('SmartContractType: spec must be presented')

        if not isinstance(data['spec'], dict):
            raise ValueError('SmartContractType: spec must be dict')

        if 'selector' not in data['spec']:
            raise ValueError('SmartContractType: selector must be presented')

        self.selector.parse(data['spec']['selector'])

        if 'get_methods' in data['spec']:
            if not isinstance(data['spec']['get_methods'], list):
                raise ValueError('SmartContractType: get_methods must be presented as list')

            for getter in data['spec']['get_methods']:
                tmp = MethodsSubtype(self.context,
                                     allow_sub_getters=True,
                                     anon_getter=self.anon_getter)
                tmp.parse(getter)
                self.get_methods.append(tmp)

    def to_dict(self):
        getters = []

        for getter in self.get_methods:
            getters.extend(getter.to_dict())

        return {
            'metadata': self.metadata.to_dict(),
            'labels': self.labels.to_dict(),
            'selector': self.selector.to_dict(),
            'get_methods': getters
        }
