import yaml
import os

from dabi.builtins import *

current_file_path = os.path.dirname(os.path.abspath(__file__))

context = dABIContext()
context.set_root(os.path.join(current_file_path, "schema"))
