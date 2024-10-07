from dabi.builtins.subtypes.metadata import MetadataSubtype
from dabi.builtins.subtypes.labels import LabelsSubtype
from dabi.builtins.subtypes.tlb import TLBSubtype
from dabi.builtins.subtypes.base import dABISubtype
import re
from collections import OrderedDict



class TVMTypeSubtype(dABISubtype):
    def __init__(self, context, anon_getter):
        super().__init__(context)

        self.metadata = MetadataSubtype(context)
        self.labels = LabelsSubtype(context)

        self.tlb = None
        self.type = None
        self.required = None
        self.items = None
        self.anon_getter = anon_getter
        self.supported_types = [
            'Null',
            'Cell',
            'Builder',
            'Slice',
            'Continuation',
            'Tuple',
            'Int',
        ]

    def parse(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError("TVMTypeSubtype expects a dict but got {}".format(type(data)))

        if 'type' not in data:
            raise ValueError("TVMTypeSubtype: must have 'type' key in data")

        if not isinstance(data['type'], str):
            raise ValueError("TVMTypeSubtype: must have 'type' as string")

        if data['type'] not in self.supported_types:
            raise ValueError("TVMTypeSubtype: type '{}' not supported".format(data['type']))

        self.type = data['type']

        if data['type'] in ['Cell', 'Builder', 'Slice']:
            if 'tlb' in data:
                if not isinstance(data['tlb'], dict):
                    raise ValueError("TVMTypeSubtype: tlb must be a dict")

                tmp = TLBSubtype(self.context)
                tmp.parse(data['tlb'])
                self.tlb = tmp
        else:
            if 'tlb' in data:
                raise ValueError("TVMTypeSubtype: tlb supported only for: Cell, Builder, Slice")

        if 'metadata' in data:
            self.metadata.parse(data['metadata'])

        if 'labels' in data:
            self.labels.parse(data['labels'])

        if self.labels.data is None:
            self.labels.data = {}

        if 'name' not in self.labels.data:
            self.labels.data['name'] = f'anon_{self.anon_getter()}'
        else:
            pattern = r'^[A-Za-z_][A-Za-z0-9_]*$'
            if re.match(pattern, self.labels.data['name']) is None:
                raise ValueError("TVMTypeSubtype: name must match pattern '{}'".format(pattern))

            if 'anon_' in self.labels.data['name']:
                raise ValueError("TVMTypeSubtype: name must not contain anon_")

        if 'required' in data:
            if not isinstance(data['required'], str) and not isinstance(data['required'], int):
                raise ValueError(
                    f"TVMTypeSubtype: must have 'required' key in data as string, not {type(data['required'])}")

            if isinstance(data['required'], int):
                data['required'] = str(data['required'])

            if self.type in ['Cell', 'Builder', 'Slice']:
                if len(data['required']) != 64:
                    raise ValueError("TVMTypeSubtype: must have 'required' length as 64 for HEX string")

                try:
                    int(data['required'], 16)
                except ValueError:
                    raise ValueError('TVMTypeSubtype: must have required as hex string')

                self.required = data['required'].upper()

            elif self.type in ['Int']:
                if '0x' in data['required']:
                    try:
                        int(data['required'], 16)
                    except ValueError:
                        raise ValueError("TVMTypeSubtype: requires required as parsable int")

                    self.required = int(data['required'], 16)
                else:
                    try:
                        int(data['required'])
                    except ValueError:
                        raise ValueError("TVMTypeSubtype: requires required as parsable int")

                    self.required = int(data['required'])

        if 'items' in data:
            if self.type != 'Tuple':
                raise ValueError("TVMTypeSubtype: items must be only for Tuple type")

            if not isinstance(data['items'], list):
                raise ValueError("TVMTypeSubtype: items must be a list")

            tmp = []
            for item in data['items']:
                t = TVMTypeSubtype(self.context, self.anon_getter)
                t.parse(item)
                tmp.append(t)

            self.items = tmp

    def to_dict(self, type_only=False):
        if type_only:
            tmp = OrderedDict()
            tmp['type'] = self.type

            if self.type == 'Tuple':
                tmp['items'] = [i.to_dict(type_only) for i in self.items]

            return tmp

        tmp = {
            'type': self.type,
            'metadata': self.metadata.to_dict(),
            'labels': self.labels.to_dict(),
            'required': self.required,
        }

        if self.tlb is not None:
            tmp['tlb'] = self.tlb.to_dict()

        if self.type == 'Tuple':
            tmp['items'] = [i.to_dict() for i in self.items]

        return tmp
