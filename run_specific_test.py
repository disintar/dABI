import os
import yaml
import sys

from dabi.builtins import dABIContext
from dabi.builtins.types.testcase import TCaseType
from dabi.parser import dABIParser

current_file_path = os.path.dirname(os.path.abspath(__file__))


def run(to_run: str = None):
    if to_run is None and len(sys.argv) < 2:
        print("Please provide ARGS0 as a command-line argument.")
        return
    elif to_run is None:
        to_run = sys.argv[1]

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
                        if tmp.name == to_run:
                            tmp.validate()
                        del tmp

    del context
    del parser
    del abi

    print('Done')


if __name__ == '__main__':
    run("tonco_pool")

