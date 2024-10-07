from tests.test_base import *

def test_selector():
    with open('examples/selector.yaml', 'r') as stream:
        selectors = list(yaml.safe_load_all(stream))
        context.update_subcontext()

        tmp = SelectorSubtype(context)
        tmp.parse(selectors[0]['selector'])
        assert tmp.to_dict() == {'selector_type': 'by_methods', 'items': []}
        context.update_subcontext()

        tmp = SelectorSubtype(context)
        tmp.parse(selectors[1]['selector'])
        assert tmp.to_dict() == {'selector_type': 'by_code', 'items': [{'metadata': {'name': '', 'description': '', 'link': ''}, 'hash': '4E4B39225F7E06D274CE590D74CB68CBCC7E679AB6D4548FA44DC37FCF9C35FD'}, {'metadata': {'name': '', 'description': '', 'link': ''}, 'hash': '004B39225F7E06D274CE590D74CB68CBCC7E679AB6D4548FA44DC37FCF9C3500'}, {'metadata': {'name': '', 'description': '', 'link': 'https://github.com/...'}, 'hash': '004B39225F7E06D274CE590D74CB68CBCC7E679AB6D4548FA44DC37FCF9C3500'}]}
