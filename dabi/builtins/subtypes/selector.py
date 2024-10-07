import base64
import binascii

from dabi.builtins.subtypes.metadata import MetadataSubtype
from dabi.builtins.subtypes.base import dABISubtype


class SelectorSubtype(dABISubtype):
    selector_type: str = False
    items: list = None

    def parse(self, data):
        if not isinstance(data, dict):
            raise ValueError('SelectorSubtype: data must be a dict')

        self.items = []

        if 'by_code' in data:
            self.selector_type = 'by_code'

            if not isinstance(data['by_code'], list):
                raise ValueError('SelectorSubtype error: by_code must be a list')

            for item in data['by_code']:
                current_item = {'metadata': MetadataSubtype(self.context)}

                if 'metadata' in item:
                    current_item['metadata'].parse(item['metadata'])

                if 'hash' not in item:
                    raise ValueError('SelectorSubtype error: hash must be present')

                if not isinstance(item['hash'], str):
                    raise ValueError('SelectorSubtype error: hash must be a string')

                if len(item['hash']) != 64:
                    try:
                        decoded_bytes = base64.b64decode(item['hash'])
                        hex_string = binascii.hexlify(decoded_bytes).decode('utf-8')
                    except Exception as e:
                        raise ValueError('SelectorSubtype error: hash must be base64 encoded or hexstring')

                    item['hash'] = hex_string.upper()
                else:
                    item['hash'] = item['hash'].upper()
                    try:
                        int(item['hash'], 16)
                    except ValueError:
                        raise ValueError('SelectorSubtype error: hash must be a hex string')

                current_item['metadata'] = current_item['metadata'].to_dict()
                current_item['hash'] = item['hash']

                self.items.append(current_item)
        elif 'by_methods' in data:
            if not isinstance(data['by_methods'], bool):
                raise ValueError('SelectorSubtype error: by_methods must be a bool')
            assert data['by_methods'], "SelectorSubtype error: by_methods is False, but other not provided"

            self.selector_type = 'by_methods'
        else:
            raise ValueError('SelectorSubtype error: selector must be either by_code or by_method')

        self.context.subcontext.set_selector(self)

    def to_dict(self):
        return {
            'selector_type': self.selector_type,
            'items': self.items
        }
