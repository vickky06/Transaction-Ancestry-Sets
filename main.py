import collections
import requests
import json

# Define global constants
HOST = "https://blockstream.info/api/"
END_POINTS = {
    "BLOCK_HEIGHT": "/block-height/",
    "BLOCK_HASH": "/block/"
}

vin_mapping = collections.defaultdict(set)


def vin_mapping_function(response): 
    for tx in response:
        for vin in tx["vin"]:
            if "txid" in vin:
                vin_mapping[tx["txid"]].add(vin["txid"])
    return vin_mapping


def get_hash(height: int) -> str:
    url = f"{HOST}{END_POINTS['BLOCK_HEIGHT']}{height}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.RequestException as e:
        print("Error getting hash:", e)
        return ""


def get_block(hash: str, start_index: int = 0) -> list:
    url = f"{HOST}{END_POINTS['BLOCK_HASH']}{hash}/txs/{start_index}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print("Error getting block:", e)
        return []


def write_response_to_json(response_data, filename: str = 'tranx_history.json'):
    try:
        with open(filename, 'w') as json_file:
            json.dump(response_data, json_file, indent=4)
        print(f"Response data written to {filename} successfully.")
    except Exception as e:
        print("Error:", e)


def update_transactions(transaction_list, dependencies):
    valid_transactions = {}

    def update_transaction(transaction):
        if transaction in valid_transactions:
            return valid_transactions[transaction]

        if transaction not in dependencies:
            valid_transactions[transaction] = []
            return []

        current_dependencies = dependencies[transaction]
        valid_dependencies = [dep for dep in current_dependencies if dep in transaction_list]

        for dep in valid_dependencies:
            valid_dependencies.extend(update_transaction(dep))

        valid_transactions[transaction] = list(set(valid_dependencies))
        return valid_dependencies

    for transaction in transaction_list:
        update_transaction(transaction)

    return valid_transactions


if __name__ == "__main__":
    BLOCK_NUMBER = 680000
    hash = get_hash(BLOCK_NUMBER)
    tranx_history = []

    while True:
        response = get_block(hash, len(tranx_history))
        tranx_history.extend(response)
        if len(response) == 0:
            break
        vin_mapping = vin_mapping_function(response)

    write_response_to_json(tranx_history)
    write_response_to_json(vin_mapping, "vin_mapping.json")

    transactions = set(vin_mapping.keys())
    updated_transactions = update_transactions(transactions, vin_mapping)
    write_response_to_json(updated_transactions, "updated_transactions.json")

    sorted_keys = sorted(updated_transactions.keys(), key=lambda x: len(updated_transactions[x]), reverse=True)
    for key in sorted_keys[:10]:
        print(f"{key}:{len(updated_transactions[key])}")
