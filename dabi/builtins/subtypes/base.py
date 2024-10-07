from dabi.builtins.base import dABI


class dABISubtype(dABI):
    parsed = False

    def parse(self, data: dict) -> bool:
        raise NotImplementedError
