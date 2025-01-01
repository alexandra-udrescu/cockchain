from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))  # Replace with your node URL
if not w3.is_connected():
    print("Failed to connect to the blockchain.")
    exit()

admin_account = w3.eth.accounts[0]

target_address = input("Enter the recipient's Ethereum address: ").strip()

amount_in_ether = 100

try:
    txn = {
        "from": admin_account,
        "to": target_address,
        "value": w3.to_wei(amount_in_ether, "ether"),
        "gas": 21000,
        "gasPrice": w3.to_wei("20", "gwei"),
        "nonce": w3.eth.get_transaction_count(admin_account),
    }

    txn_hash = w3.eth.send_transaction(txn)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    print(f"Transaction successful! Hash: {txn_hash.hex()}")
    print(f"Transferred {amount_in_ether} Ether to {target_address}.")
except Exception as e:
    print(f"Transaction failed: {str(e)}")
