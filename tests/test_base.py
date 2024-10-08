import yaml
import sys
import os
from os.path import dirname as d
from os.path import abspath

root_dir = d(d(abspath(__file__)))
sys.path.append(root_dir)

from dabi.builtins import *

current_file_path = os.path.dirname(os.path.abspath(__file__))

context = dABIContext()
context.set_root(os.path.join(current_file_path, "schema"))
