from dabi.builtins.context import dABIContext


class dABI:
    def __init__(self, context: dABIContext):
        self.context: dABIContext = context

    def to_dict(self):
        raise NotImplementedError
