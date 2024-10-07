import hashlib
import uuid
from typing import Optional


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

    def register_tlb(self, tlb: str, tlb_path: str = None) -> str:

        if tlb_path is None:
            my_id = uuid.uuid4().hex
        else:
            my_id = hashlib.sha256(tlb_path.encode('utf-8')).hexdigest().upper()

        self.tlb_sources[my_id] = tlb
        return my_id

    def set_root(self, root):
        self.root = root

    def update_subcontext(self):
        self.subcontext = dABISubContext()
