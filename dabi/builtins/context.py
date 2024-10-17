import hashlib
import textwrap
import uuid
from typing import Optional
from jinja2 import Environment
import os
import io


def get_method_wrapper(root):
    def get_method(filename, indent):
        with open(os.path.join(root, 'get_methods', filename), 'r') as file:
            text = file.read()

            lines = text.splitlines()

            if len(lines) > 1:
                indented_text = lines[0] + '\n' + textwrap.indent('\n'.join(lines[1:]), ' ' * indent)
            else:
                indented_text = lines[0]

            return indented_text

    return get_method


def load_smart_contract_template(root, smc_yaml):
    env = Environment()
    env.globals['get_method'] = get_method_wrapper(root)

    template = env.from_string(smc_yaml)
    rendered_template = template.render()

    return io.StringIO(rendered_template)


class dABISubContext:
    selector = None

    def set_selector(self, selector):
        if self.selector is not None:
            raise ValueError(f"DABISubContext: can't have two selectors at the same time")

        self.selector = selector


class dABIContext:
    def __init__(self):
        self.root = '.'
        self.tlb_sources = {}

        self.subcontext: Optional[dABISubContext] = None
        self.smcs_names = set()

    def load_block(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'block.tlb')) as f:
            self.tlb_sources['block_tlb'] = f.read()

    def register_tlb(self, tlb: str, tlb_path: str = None, tlb_version="tlb/v0", use_block_tlb: bool = False) -> str:
        if tlb_path is None:
            my_id = uuid.uuid4().hex
        else:
            my_id = hashlib.sha256(tlb_path.encode('utf-8')).hexdigest().upper()

        if use_block_tlb and 'block_tlb' not in self.tlb_sources:
            self.load_block()

        self.tlb_sources[my_id] = {
            'version': tlb_version,
            'tlb': tlb,
            'use_block_tlb': use_block_tlb
        }

        return my_id

    def set_root(self, root):
        self.root = root

    def register_smc(self, name):
        if name not in self.smcs_names:
            self.smcs_names.add(name)
        else:
            raise ValueError(f"DABISubContext: duplicate smc: {name}")

    def update_subcontext(self):
        self.subcontext = dABISubContext()
