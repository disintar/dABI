import hashlib
from typing import List
import json

from tonpy import method_name_to_id

from dabi.builtins.subtypes.labels import LabelsSubtype
from dabi.builtins.subtypes.metadata import MetadataSubtype
from dabi.builtins.subtypes.base import dABISubtype
from dabi.builtins.subtypes.tvm_types import TVMTypeSubtype
from dabi.builtins.types.base import dABIType
from dabi.settings import supported_versions


class MethodsSubtype(dABISubtype):
    method_inline = False
    full_get_method = None

    method_name = None
    method_id = None
    result_strict_type_check = True
    result_length_strict_check = True
    method_result = None
    method_args = None

    def __init__(self, context,
                 allow_sub_getters,
                 anon_getter):
        super().__init__(context)
        self.labels = LabelsSubtype(context)
        self.metadata = MetadataSubtype(context)
        self.allow_sub_getters = allow_sub_getters
        self.anon_getter = anon_getter

    def parse(self, data: dict):
        if 'method_name' in data:
            self.method_inline = True

            if not isinstance(data['method_name'], str):
                raise ValueError('MethodsSubtype: method_name must be a string')

            self.method_name = data['method_name']
            self.method_id = method_name_to_id(data['method_name'])
            if 'metadata' in data:
                self.metadata.parse(data['metadata'])

            if 'labels' in data:
                self.labels.parse(data['labels'])

            self.method_args = []
            self.method_result = []

            for i in ['result_length_strict_check', 'result_strict_type_check']:
                if i in data:
                    if not isinstance(data[i], bool):
                        raise ValueError(f'MethodsSubtype: {i} must be a boolean')

                    setattr(self, i, data[i])

            l = {'args': self.method_args, 'result': self.method_result}

            for k in l:
                if k in data:
                    if not isinstance(data[k], list):
                        raise ValueError('MethodsSubtype: args must be a list')

                    for arg in data[k]:
                        tmp = TVMTypeSubtype(self.context, self.anon_getter)
                        tmp.parse(arg)
                        l[k].append(tmp)

        else:
            raise ValueError('MethodsSubtype: Method name missing')

    def to_dict(self) -> List:
        self.calculate_hash()

        args_hash, result_hash = self.calculate_hash()

        return [{
            'metadata': self.metadata.to_dict(),
            'labels': self.labels.to_dict(),

            'method_name': self.method_name,
            'method_id': self.method_id,
            'method_args': [i.to_dict() for i in self.method_args],
            'method_result': [i.to_dict() for i in self.method_result],

            'method_args_hash': args_hash,
            'method_result_hash': result_hash,

            'result_strict_type_check': self.result_strict_type_check,
            'result_length_strict_check': self.result_length_strict_check
        }]

    def calculate_hash(self):
        json_string_args = json.dumps({'stack': [i.to_dict(True) for i in self.method_args]},
                                      separators=(',', ':'))
        json_string_result = json.dumps({'stack': [i.to_dict(True) for i in self.method_result]},
                                        separators=(',', ':'))

        args_hash = hashlib.sha256(json_string_args.encode('utf-8')).hexdigest().upper()
        result_hash = hashlib.sha256(json_string_result.encode('utf-8')).hexdigest().upper()

        return args_hash, result_hash


class GetMethodType(dABIType):
    def __init__(self, context, allow_sub_getters=True, anon_getter=None):
        super().__init__(context)
        self.labels = LabelsSubtype(context)
        self.metadata = MetadataSubtype(context)
        self.methods: List[MethodsSubtype] = []
        self.allow_sub_getters = allow_sub_getters
        self.anon_names = 0
        self.unique_names = set()
        self.anon_getter = anon_getter

    def parse(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError('GetMethodType: data must be a dict')

        assert data['type'] == "GetMethod"
        assert data['apiVersion'] in supported_versions, "GetMethodType API version must be supported"

        if 'labels' in data:
            self.labels.parse(data['labels'])

        if 'metadata' in data:
            self.metadata.parse(data['metadata'])

        if 'spec' not in data:
            raise ValueError('GetMethodType: data must contain a spec')

        if not isinstance(data['spec'], list):
            raise ValueError('GetMethodType: spec must be a list')

        for spec in data['spec']:
            tmp = MethodsSubtype(self.context,
                                 allow_sub_getters=self.allow_sub_getters,
                                 anon_getter=self.anon_getter)
            tmp.parse(spec)

            self.methods.append(tmp)

    def to_dict(self):
        result_methods = []

        for i in self.methods:
            i.metadata += self.metadata
            i.labels += self.labels

            result_methods.extend(i.to_dict())

        return result_methods
