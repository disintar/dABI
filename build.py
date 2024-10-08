from pprint import pprint

from dabi.parser import dABIParser
import os

current_file_path = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    parser = dABIParser(current_file_path)
    result_json = parser.parse()
    pprint(result_json)
