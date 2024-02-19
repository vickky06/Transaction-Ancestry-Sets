import collections
import requests
import json
# import os

# Define global constants
HOST = "https://blockstream.info/api/"
END_POINTS = {
    "BLOCK_HEIGHT": "/block-height/",
    "BLOCK_HASH": "/block/"
}
CACHE_DIRECTORY = "cache"
vin_mapping = collections.defaultdict(set)


def find_overlapping_keys_and_values(dictionary):
    # Extract keys and values from the dictionary
    # print(dictionary.keys())
    keys_set = set(dictionary.keys())
    values_set = set()
    for values in list(dictionary.values()):
        values_set.update(values)

    # Find the intersection between keys and values
    overlapping = keys_set.intersection(values_set)

    return len(overlapping)

def write_response_to_json(response_data, filename: str = 'tranx_history.json'):
    try:
        # Open the file in write mode and write the response data as JSON
        with open(filename, 'w') as json_file:
            
            json.dump(response_data, json_file, indent=4)
        print(f"Response data written to {filename} successfully.")
    except Exception as e:
        print("Error:", e)


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
    print(f"url : {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except requests.RequestException as e:
        print("Error getting block:", e)
        return []


# def get_txids(transactions):
#     txid_set = set()
#     for tx in transactions:
#         for vin in tx["vin"]:
#             if "txid" in vin:
#                 txid_set.add(vin["txid"])
    return txid_set

def vin_mapping_function(response): 
    for tx in response:
        for vin in tx["vin"]:
            if "txid" in vin:
                # vin_mapping[vin["txid"]].append(tx["txid"])
                vin_mapping[tx["txid"]].add(vin["txid"])
    return vin_mapping
    
def convert_sets_to_lists(d):
    for key, value in d.items():
        if isinstance(value, set):
            d[key] = list(value)
        elif isinstance(value, dict):
            convert_sets_to_lists(value)

# Convert sets to lists

def update_transactions(transaction_list, dependencies):
    # Initialize a dictionary to keep track of valid transactions
    valid_transactions = {}

    # Helper function to recursively update transactions
    def update_transaction(transaction):
        # If the transaction has already been processed, return its valid dependencies
        if transaction in valid_transactions:
            return valid_transactions[transaction]

        # If the transaction is not in the dependencies, it is a leaf node
        if transaction not in dependencies:
            valid_transactions[transaction] = []
            return []

        # Get the dependencies of the current transaction
        current_dependencies = dependencies[transaction]

        # Filter out dependencies that are not in the transaction list
        valid_dependencies = [dep for dep in current_dependencies if dep in transaction_list]

        # Recursively update dependencies
        for dep in valid_dependencies:
            valid_dependencies.extend(update_transaction(dep))

        # Remove duplicates and update valid transactions
        valid_transactions[transaction] = list(set(valid_dependencies))

        return valid_dependencies

    # Iterate through each transaction in the transaction list
    for transaction in transaction_list:
        update_transaction(transaction)

    return valid_transactions


        





if __name__ == "__main__":
    # # Create cache directory if it doesn't exist
    # if not os.path.exists(CACHE_DIRECTORY):
    #     os.makedirs(CACHE_DIRECTORY)

    # all_txIds = set()
    BLOCK_NUMBER = 680000
    hash = get_hash(BLOCK_NUMBER)
    print(f"hash : {hash}")
    tranx_history = []

    while True:
        response = get_block(hash, len(tranx_history))
        tranx_history.extend(response)
        if len(response) == 0:
            break
        vin_mapping = vin_mapping_function(response)

    # Write response to JSON file
    write_response_to_json(tranx_history)
    convert_sets_to_lists(vin_mapping)
    write_response_to_json(vin_mapping,"vin_mapping.json")


    # Open the JSON file and read its contents
    # with open(file_path, 'r') as file:
    #     # Load the JSON data into a Python dictionary
    #     data = json.load(file)
    data = vin_mapping;
    transactions = set(data.keys())
    updated_transactions = update_transactions(transactions, data)
    write_response_to_json(updated_transactions,"updated_transactions.json")
    sorted_keys = sorted(updated_transactions.keys(), key=lambda x: len(updated_transactions[x]), reverse=True)
    for key in sorted_keys[:10]:
        print(f"{key}:{len(updated_transactions[key])}")

    '''
    7d08f0c61cda9379bdf1fa68095f827199a0d4cb6b466a6da3f0dc956772c52b:14
    b2bab595112517e8b6a06aa9f616272b479e57e21b4da52877ddf385316aa19b:13
    d294be35db0b5fab4a6a00d6e4441c7e54be88fa02dfc188b75e4604ec6c3fcf:12
    4205c68c68266259c5723948e0407dff25600e6420659cef4286dd1ae4658b63:12
    7a128b0242d89d327fc2c273199c7529a31477d8ea949e5176b2a4eb69b74464:12
    7841dc7cf61d394094f4341fa98d0a6fd771e95ac93a9dcfec12a23ed3c670c5:12
    973e5adb05cc1cb80cabc5e451200333c993034153a078733ec06af7bf3c860b:11
    ef6c8e97b62eced1913df503667d49b9f5890cdb201be5d5d6c304af1d3f5db1:11
    afe4b90e667df0171f63e6cc95c0a12d24592d436dd2e8b9b2a9998b4099ff6d:11
    4b4c90943c1651eabb8c5dfb6f490c4e56bd6cf42950a0430db17b9691b0236c:11
    '''



'''
vin_mapping: 
{
    transID: [vin list]

}

t_set = set<transID>

iterate over vin_mapping:  T_ID: 
    for each vin should be in t_set:
    vin_mapping[T_ID].add(vin)
    if not : skip


txns list: [A, B, C, D, E]

txn A: { vin: [B, C]}
txn B: { vin: [X, Y, E]}
txn C: {vin: [R]}
txn D: {vin: [S]}
txn E: {vin: [Q]}

'''