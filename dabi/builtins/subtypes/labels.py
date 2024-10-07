from dabi.builtins.subtypes.base import dABISubtype


class LabelsSubtype(dABISubtype):
    data: dict = None

    def parse(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError('LabelsSubtype error: data must be a dict')

        self.data = data

    def to_dict(self):
        return self.data

    def __add__(self, other):
        if not isinstance(other, LabelsSubtype):
            return NotImplemented

        left_data = self.data if self.data is not None else {}
        right_data = other.data if other.data is not None else {}

        merged_data = {**right_data, **left_data}

        tmp = LabelsSubtype(self.context)
        tmp.data = merged_data

        return tmp
