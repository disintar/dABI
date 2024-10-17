import json
import os
import argparse
from dabi.parser import dABIParser

current_file_path = os.path.dirname(os.path.abspath(__file__))


def main(allow_empty_code, minify):
    parser = dABIParser(current_file_path, allow_empty_code=allow_empty_code)
    result_json = parser.parse()

    if minify:
        print(json.dumps(result_json, separators=(',', ':')))
    else:
        print(json.dumps(result_json, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="dABI Parser Script")
    parser.add_argument("--not-allow-empty-code", action="store_true", help="Disallow parsing with empty code")
    parser.add_argument("--minify", action="store_true", help="Minify the output JSON")
    args = parser.parse_args()
    main(not args.not_allow_empty_code, args.minify)
