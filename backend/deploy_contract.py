from web3 import Web3
import json

print("Connecting to blockchain...")
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

if w3.is_connected():
    print("Successfully connected to blockchain!")
else:
    print("Failed to connect to blockchain. Make sure Ganache is running.")
    exit()

print("Loading ABI and bytecode...")
try:
    with open('build/FlagSubmission.abi', 'r') as abi_file:
        contract_abi = json.loads(abi_file.read())

    with open('build/FlagSubmission.bin', 'r') as bin_file:
        contract_bytecode = '0x' + bin_file.read().strip()

    print("ABI and bytecode loaded successfully.")
except Exception as e:
    print(f"Error loading ABI or bytecode: {e}")
    exit()

def deploy_contract():
    try:
        print("Getting account...")
        account = w3.eth.accounts[0]
        print(f"Using account: {account}")
        print(f"Balance: {w3.eth.get_balance(account)} wei")

        print("Preparing contract...")
        FlagSubmission = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)

        print("Deploying contract...")
        tx_hash = FlagSubmission.constructor().transact({
            'from': account,
            'gas': 3000000,
            'gasPrice': Web3.to_wei('20', 'gwei')
        })

        print(f"Transaction hash: {tx_hash.hex()}")

        print("Waiting for transaction receipt...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f'Contract deployed at address: {tx_receipt.contractAddress}')
        return tx_receipt.contractAddress
    except Exception as e:
        print(f"Error deploying contract: {e}")
        exit()

print("Starting deployment process...")
deployed_address = deploy_contract()
print(f"Contract successfully deployed at: {deployed_address}")
