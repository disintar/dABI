import os
import yaml

from dabi.builtins import dABIContext
from dabi.builtins.types.testcase import TCaseType
from dabi.parser import dABIParser

current_file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_build():
    parser = dABIParser(current_file_path)
    abi = parser.parse()

    context = dABIContext()

    context.set_root(current_file_path)
    for subdir, dirs, files in os.walk(os.path.join(context.root, "schema", "tests")):
        for file in files:
            if file.endswith('.yaml'):
                with open(os.path.join(subdir, file), 'r') as stream:
                    smcs = list(yaml.safe_load_all(stream))

                    for smc in smcs:
                        context.update_subcontext()
                        tmp = TCaseType(context, abi)
                        tmp.parse(smc)
                        tmp.validate()
