import json
import sys


def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)


def compare_smart_contract_names(a_contracts, b_contracts):
    """Compare smart contract names between two JSON objects."""
    a_names = {contract['metadata']['name'] for contract in a_contracts}
    b_names = {contract['metadata']['name'] for contract in b_contracts}

    added_names = b_names - a_names
    removed_names = a_names - b_names

    return added_names, removed_names


def compare_method_names(a_contracts, b_contracts):
    """Compare get_methods method names in two JSON objects."""
    a_methods = {method['method_name'] for contract in a_contracts for method in contract['get_methods']}
    b_methods = {method['method_name'] for contract in b_contracts for method in contract['get_methods']}

    added_methods = b_methods - a_methods
    removed_methods = a_methods - b_methods

    return added_methods, removed_methods


def main():
    if len(sys.argv) != 3:
        print("Usage: python diff.py a.json b.json")
        sys.exit(1)

    a_file = sys.argv[1]
    b_file = sys.argv[2]

    # Load the two JSON files
    a_data = load_json(a_file)
    b_data = load_json(b_file)

    # Compare smart contract names
    added_names, removed_names = compare_smart_contract_names(
        a_data.get('smart_contracts', []), b_data.get('smart_contracts', []))

    # Compare get_methods method names
    added_methods, removed_methods = compare_method_names(
        a_data.get('smart_contracts', []), b_data.get('smart_contracts', []))

    # Print the results
    print("Added Smart Contracts:")
    for name in added_names:
        print(f"- {name}")

    print("\nRemoved Smart Contracts:")
    for name in removed_names:
        print(f"- {name}")

    print("\nAdded Method Names:")
    for method in added_methods:
        print(f"- {method}")

    print("\nRemoved Method Names:")
    for method in removed_methods:
        print(f"- {method}")


if __name__ == "__main__":
    main()
