from dabi.builtins.subtypes.base import dABISubtype


class MetadataSubtype(dABISubtype):
    name = ''
    description = ''
    link = ''

    def parse(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError('MetadataSubtype: data must be a dict')

        if 'name' in data:
            if not isinstance(data['name'], str):
                raise ValueError('MetadataSubtype: name must be a str')

            self.name = data['name']

        if 'description' in data:
            if not isinstance(data['description'], str):
                raise ValueError('MetadataSubtype: description must be a str')

            self.description = data['description']

        if 'link' in data:
            if not isinstance(data['link'], str):
                raise ValueError('MetadataSubtype: link must be a str')

            self.link = data['link']

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'link': self.link
        }

    def __add__(self, other):
        if not isinstance(other, MetadataSubtype):
            return NotImplemented

        tmp = MetadataSubtype(self.context)
        for attr in ['name', 'description', 'link']:
            setattr(tmp, attr, getattr(self, attr) or getattr(other, attr))

        return tmp
