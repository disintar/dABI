import hashlib
import textwrap
import uuid
from typing import Optional
from jinja2 import Environment
import os
import io
import yaml


def load_yaml_files(root):
    """Loads all YAML files from the 'constants' directory and returns a dictionary."""
    yaml_data = {}

    for subdir, _, files in os.walk(os.path.join(root, 'constants')):
        for file in files:
            if file.endswith('.yaml'):
                filepath = os.path.join(subdir, file)
                with open(filepath, 'r') as f:
                    # Load all documents in a YAML file (handle multiple items in one file)
                    docs = list(yaml.safe_load_all(f))
                    for doc in docs:
                        if isinstance(doc, dict):
                            # Extract the key from each document, assuming it has one top-level key
                            for key, value in doc.items():
                                yaml_data[key] = value

    return yaml_data


def get_method_wrapper(root, yaml_data):
    def get_method(keys, indent=0):
        """Return YAML content by key(s) with optional indentation, excluding the key itself."""
        if isinstance(keys, str):
            keys = [keys]

        # Collect the content by keys without including the keys themselves
        merged_content = []
        for key in keys:
            content = yaml_data.get(key, None)
            if content is None:
                raise KeyError(f"No such key: {key} in loaded YAML data")

            # Add the content without the key itself (only the value under the key)
            merged_content.append(content)

        # If there are multiple pieces of content, merge them as needed
        if len(merged_content) == 1:
            merged_content = merged_content[0]
        else:
            # Merging content might depend on your specific requirements, here's just a concatenation
            merged_content = merged_content

        # Convert the merged YAML content to text with optional indentation
        text = yaml.dump(merged_content, default_flow_style=False)
        lines = text.splitlines()

        if len(lines) > 1:
            indented_text = lines[0] + '\n' + textwrap.indent('\n'.join(lines[1:]), ' ' * indent)
        else:
            indented_text = lines[0]

        return indented_text

    return get_method


def load_smart_contract_template(root, smc_yaml):
    # Load all YAML files from the 'constants' folder and extract keys
    yaml_data = load_yaml_files(root)

    # Set up the Jinja2 environment
    env = Environment()

    # Make the constants method available in Jinja2
    env.globals['constants'] = get_method_wrapper(root, yaml_data)

    # Load and render the template
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
