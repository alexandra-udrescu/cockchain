import os
import json
from eth_keys import keys
from datetime import datetime

def create_wallet(username):
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

    base_filename = f"wallets/{username.lower()}_wallet.json"
    filename = base_filename

    if os.path.exists(filename):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"wallets/{username.lower()}_wallet_{timestamp}.json"

    with open(filename, "w") as wallet_file:
        json.dump(wallet_data, wallet_file, indent=4)

    print(f"Wallet file '{filename}' created successfully!")
    print(f"Address: {address}")

user_input = input("Enter a username for your wallet: ")
create_wallet(user_input)
