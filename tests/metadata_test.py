from test_base import *


def test_metadata():
    with open('tests/examples/metadata.yaml', 'r') as stream:
        meatadatas = list(yaml.safe_load_all(stream))
        context.update_subcontext()

        c = MetadataSubtype(context)
        c.parse(meatadatas[0]['metadata'])
        assert c.to_dict() == {'name': 'Test', 'description': '', 'link': ''}
        context.update_subcontext()

        c = MetadataSubtype(context)
        c.parse(meatadatas[1]['metadata'])
        assert c.to_dict() == {'name': 'Test', 'description': 'Test description lolkek\n', 'link': 'https://ya.ru/'}
