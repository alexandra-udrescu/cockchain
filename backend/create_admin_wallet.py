import os
import json
from web3 import Web3
from eth_keys import keys

web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
if not web3.is_connected():
    raise Exception("Failed to connect to the blockchain. Make sure Ganache or your Ethereum node is running.")

with open("build/FlagSubmission.abi", "r") as abi_file:
    contract_abi = json.load(abi_file)

# REPLACE THIS WITH YOUR CONTRACT ADDRESS
contract_address = "0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab"
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Admin account setup (this account must already be an admin in the contract)
admin_account = web3.eth.accounts[0]
web3.eth.default_account = admin_account

def create_wallet(username):
    """Create a wallet for the admin."""
    private_key_bytes = os.urandom(32)
    private_key = keys.PrivateKey(private_key_bytes)
    public_key = private_key.public_key
    address = public_key.to_checksum_address()

    wallet_data = {
        "username": username,
        "private_key": private_key.to_hex(),
        "public_key": public_key.to_hex(),
        "address": address
    }

    if not os.path.exists("wallets"):
        os.makedirs("wallets")

    wallet_file_path = f"wallets/{username.lower()}_admin_wallet.json"
    with open(wallet_file_path, "w") as wallet_file:
        json.dump(wallet_data, wallet_file, indent=4)

    print(f"Admin wallet created: {wallet_file_path}")
    print(f"Address: {address}")
    return address

def add_admin(new_admin):
    """Add a new admin to the contract."""
    print(f"Adding admin: {new_admin}")
    try:
        tx_hash = contract.functions.addAdmin(new_admin).transact({'from': admin_account, 'gas': 5000000})
        web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Admin added: {new_admin}")
    except Exception as e:
        print(f"Failed to add admin: {e}")

def fund_user(target_address, amount_in_ether):
    """Fund a target Ethereum address with Ether."""
    if not Web3.is_address(target_address):
        print(f"Invalid Ethereum address: {target_address}")
        return

    try:
        txn = {
            "from": admin_account,
            "to": target_address,
            "value": web3.to_wei(amount_in_ether, "ether"),
            "gas": 21000,
            "gasPrice": web3.to_wei("20", "gwei"),
            "nonce": web3.eth.get_transaction_count(admin_account),
        }

        txn_hash = web3.eth.send_transaction(txn)
        receipt = web3.eth.wait_for_transaction_receipt(txn_hash)

        print(f"Transaction successful! Hash: {txn_hash.hex()}")
        print(f"Transferred {amount_in_ether} Ether to {target_address}.")
    except Exception as e:
        print(f"Transaction failed: {str(e)}")

if __name__ == "__main__":
    print("rawr xD Admin Wallet Creation Script xoxo")
    username = input("Enter a username for the new admin: ").strip()

    admin_wallet_address = create_wallet(username)

    print("Adding the wallet address to the contract as an admin...")
    add_admin(admin_wallet_address)

    print("Funding the new admin wallet...")
    fund_user(admin_wallet_address, 100)

    print("Admin setup complete.")
