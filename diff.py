import json
import sys


def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)


def compare_smart_contracts(a_contracts, b_contracts):
    """Compare smart contract metadata between two JSON objects."""
    a_contracts_metadata = {contract['metadata']['name']: contract for contract in a_contracts}
    b_contracts_metadata = {contract['metadata']['name']: contract for contract in b_contracts}

    added_contracts = {name: b_contracts_metadata[name] for name in b_contracts_metadata if
                       name not in a_contracts_metadata}
    removed_contracts = {name: a_contracts_metadata[name] for name in a_contracts_metadata if
                         name not in b_contracts_metadata}

    return added_contracts, removed_contracts


def compare_methods(a_contracts, b_contracts):
    """Compare get_methods methods between two JSON objects."""
    a_methods_metadata = {}
    b_methods_metadata = {}

    for contract in a_contracts:
        for method in contract.get('get_methods', []):
            a_methods_metadata[method['method_name']] = method['metadata']

    for contract in b_contracts:
        for method in contract.get('get_methods', []):
            b_methods_metadata[method['method_name']] = method['metadata']

    added_methods = {name: b_methods_metadata[name] for name in b_methods_metadata if name not in a_methods_metadata}
    removed_methods = {name: a_methods_metadata[name] for name in a_methods_metadata if name not in b_methods_metadata}

    return added_methods, removed_methods


def format_metadata(metadata):
    """Format metadata into a readable string for the markdown table."""
    name = metadata.get('name', 'No name')
    description = metadata.get('description', 'No description')
    link = metadata.get('link', '')

    link_str = f"[Link]({link})" if link else "No link"
    return f"{name} | {description} | {link_str}"


def generate_markdown_table(added, removed, category):
    """Generate a markdown table for added and removed items with metadata."""
    table = f"### {category} Changes\n\n"
    table += "| Change Type | Name | Description | Link |\n"
    table += "| ----------- | ---- | ----------- | ---- |\n"

    if added:
        for name, metadata in added.items():
            formatted_metadata = format_metadata(metadata)
            table += f"| Added 📈 | {name} | {formatted_metadata} |\n"

    if removed:
        for name, metadata in removed.items():
            formatted_metadata = format_metadata(metadata)
            table += f"| Removed 📉 | {name} | {formatted_metadata} |\n"

    if not added and not removed:
        table += "| No changes | 😊 | | |\n"

    return table


def display_contracts_info(contracts):
    """Display smart contracts and their methods."""
    table = "### Supported Smart Contracts\n\n"
    table += "| Name | Description | Selector Type | Methods |\n"
    table += "| ---- | ----------- | ------------- | ------- |\n"

    for contract in contracts:
        name = contract['metadata'].get('name', 'No name')
        description = contract['metadata'].get('description', 'No description')
        selector_type = contract.get('selector', {}).get('selector_type', 'No selector')
        methods = ", ".join([method['method_name'] for method in contract.get('get_methods', [])]) or 'No methods'
        table += f"| {name} | {description} | {selector_type} | {methods} |\n"

    return table


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python diff.py <a.json> [b.json]")
        sys.exit(1)

    a_file = sys.argv[1]
    b_file = sys.argv[2] if len(sys.argv) == 3 else None

    # Load the first JSON file
    a_data = load_json(a_file)

    if b_file:
        # Load the second JSON file
        b_data = load_json(b_file)

        key = 'by_name'
        adata = a_data.get(key, {})
        bdata = b_data.get(key, {})
        adata = [adata[i] for i in adata]
        bdata = [bdata[i] for i in bdata]

        added_contracts, removed_contracts = compare_smart_contracts(adata, bdata)
        added_methods, removed_methods = compare_methods(adata, bdata)

        contracts_table = generate_markdown_table(added_contracts, removed_contracts, "Smart Contracts")
        methods_table = generate_markdown_table(added_methods, removed_methods, "Method Names")

        print(contracts_table)
        print("\n")
        print(methods_table)

        contracts_table = display_contracts_info(adata)
        print(contracts_table)
    else:
        key = 'by_name'
        data = a_data.get(key, {})
        contracts_table = display_contracts_info([data[i] for i in data])
        print(contracts_table)


if __name__ == "__main__":
    main()
