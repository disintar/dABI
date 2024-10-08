import os.path

from dabi.builtins.subtypes.base import dABISubtype
from tonpy.tlb_gen.py import add_tlb

from dabi.settings import supported_versions


class TLBSubtype(dABISubtype):
    is_inline = False
    file_path = ''
    object = ''
    inline = ''

    tlb_version = "tlb/v0"
    tlb_id = ''
    tlb_object = ''

    def parse(self, data):
        if not isinstance(data, dict):
            raise ValueError('TLBSubtype: data must be a dict')

        if 'version' in data:
            if isinstance(data['version'], str):
                if data.get('version') in supported_versions:
                    self.tlb_version = data['version']
                else:
                    raise ValueError('TLBSubtype: version must be supported')
            else:
                raise ValueError('TLBSubtype: version must be a string')

        self.is_inline = 'inline' in data

        if not self.is_inline and 'file_path' not in data:
            raise ValueError('Invalid TLB Subtype, define inline or file_path')

        if not self.is_inline and 'object' not in data:
            raise ValueError('Invalid TLB Subtype, define object for file_path')

        if self.is_inline:
            self.inline = data.get('inline')
            if not isinstance(self.inline, str):
                raise ValueError('Invalid TLB Subtype, define inline with string')

            parsed_tlb = {}
            add_tlb(self.inline, parsed_tlb)

            if 'object' not in data:
                if len(parsed_tlb) > 1:
                    raise ValueError('Invalid TLB Subtype, define object for inline, founded more than one object')
                else:
                    self.tlb_object = list(parsed_tlb.keys())[0]
            else:
                if not isinstance(data.get('object'), str):
                    raise ValueError('Invalid TLB Subtype, define object as string')

                if data.get('object') not in parsed_tlb:
                    raise ValueError('Invalid TLB Subtype, defined object is not in TLB')

                self.tlb_object = data['object']

            self.tlb_id = self.context.register_tlb(self.inline)
        else:
            if not isinstance(data.get('file_path'), str):
                raise ValueError('Invalid TLB Subtype, define file_path as string')

            self.file_path = os.path.join(self.context.root, 'tlb', data.get('file_path'))

            if not os.path.isfile(self.file_path):
                raise ValueError(f'Invalid TLB Subtype, defined file_path does not exist: {self.file_path}')

            with open(self.file_path, 'r') as f:
                tlb_data = f.read()

                parsed_tlb = {}
                add_tlb(tlb_data, parsed_tlb)

                if not isinstance(data['object'], str):
                    raise ValueError('Invalid TLB Subtype, define object as string')

                if data.get('object') not in parsed_tlb:
                    raise ValueError('Invalid TLB Subtype, defined object is not in TLB')

                self.tlb_object = data['object']
                self.tlb_id = self.context.register_tlb(tlb_data, data.get('file_path'))

    def to_dict(self):
        return {
            'id': self.tlb_id,
            'object': self.tlb_object
        }
