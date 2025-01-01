from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
if not w3.is_connected():
    print("Failed to connect to the blockchain. Make sure Ganache is running.")
    exit()
else:
    print("Connected to blockchain!")

with open('build/FlagSubmission.abi', 'r') as abi_file:
    contract_abi = json.load(abi_file)

contract_address = '0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab'

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

admin_account = w3.eth.accounts[0]
new_admin_account = w3.eth.accounts[1]
user1_account = w3.eth.accounts[2]
user2_account = w3.eth.accounts[3]

challenges = [
    {
        "id": "challenge1",
        "title": "Basic Flag Submission",
        "category": "OSINT",
        "description": "Submit the correct flag for this challenge.",
        "flag": "flag1",
        "points": 100
    },
    {
        "id": "challenge2",
        "title": "Advanced Flag Submission",
        "category": "PWN",
        "description": "Submit the advanced flag for this challenge.",
        "flag": "flag2",
        "points": 200
    }
]

def add_admin(new_admin):
    print(f"Adding admin: {new_admin}")
    try:
        tx_hash = contract.functions.addAdmin(new_admin).transact({'from': admin_account, 'gas': 5000000})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Admin added: {new_admin}")
    except Exception as e:
        print(f"Failed to add admin: {e}")

def remove_admin(admin_to_remove):
    print(f"Removing admin: {admin_to_remove}")
    try:
        tx_hash = contract.functions.removeAdmin(admin_to_remove).transact({'from': admin_account, 'gas': 5000000})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Admin removed: {admin_to_remove}")
    except Exception as e:
        print(f"Failed to remove admin: {e}")

def get_all_admins():
    try:
        admins = contract.functions.getAllAdmins().call()
        print("Admins:")
        for admin in admins:
            print(admin)
    except Exception as e:
        print(f"Failed to fetch all admins: {e}")

def add_challenge(challenge):
    print(f"Adding challenge with ID: {challenge['id']}")
    try:
        tx_hash = contract.functions.addChallenge(
            challenge["id"],
            challenge["title"],
            challenge["category"],
            challenge["description"],
            challenge["flag"],
            challenge["points"]
        ).transact({'from': admin_account, 'gas': 5000000})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Challenge added: {challenge['id']}")
    except Exception as e:
        print(f"Failed to add challenge {challenge['id']}: {e}")

def update_challenge(challenge):
    print(f"Updating challenge with ID: {challenge['id']}")
    try:
        tx_hash = contract.functions.updateChallenge(
            challenge["id"],
            challenge["title"],
            challenge["category"],
            challenge["description"],
            challenge["flag"],
            challenge["points"]
        ).transact({'from': admin_account, 'gas': 5000000})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Challenge updated: {challenge['id']}")
    except Exception as e:
        print(f"Failed to update challenge {challenge['id']}: {e}")

def delete_challenge(challenge_id):
    print(f"Deleting challenge with ID: {challenge_id}")
    try:
        tx_hash = contract.functions.deleteChallenge(challenge_id).transact({'from': admin_account, 'gas': 5000000})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Challenge deleted: {challenge_id}")
    except Exception as e:
        print(f"Failed to delete challenge {challenge_id}: {e}")

def submit_flag(user_account, challenge_id, flag):
    print(f"User {user_account} submitting flag: {flag} for challenge: {challenge_id}")
    try:
        tx_hash = contract.functions.submitFlag(challenge_id, flag).transact({'from': user_account, 'gas': 5000000})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Flag submitted successfully for {challenge_id}")
    except Exception as e:
        print(f"Flag submission failed for {challenge_id}: {e}")

def get_solvers(challenge_id):
    try:
        solvers = contract.functions.getSolvers(challenge_id).call()
        print(f"Solvers for {challenge_id}: {solvers}")
    except Exception as e:
        print(f"Failed to fetch solvers: {e}")

def get_user_points(user_account):
    try:
        points = contract.functions.getUserPoints(user_account).call()
        print(f"User {user_account} has {points} points")
    except Exception as e:
        print(f"Failed to fetch user points: {e}")

def get_all_challenges():
    try:
        challenges = contract.functions.getAllChallenges().call()
        print("All challenges:")
        for challenge in challenges:
            print(f"ID: {challenge[0]}, Title: {challenge[1]}, Description: {challenge[2]}, Points: {challenge[5]}")
    except Exception as e:
        print(f"Failed to fetch all challenges: {e}")

def get_user_solves(user_account):
    try:
        solves = contract.functions.getUserSolves(user_account).call()
        print(f"Challenges solved by {user_account}:")
        for solve in solves:
            print(f"ID: {solve[0]}, Title: {solve[1]}, Category: {solve[2]}, Points: {solve[5]}")
    except Exception as e:
        print(f"Failed to fetch solves for {user_account}: {e}")

def main():
    print("Starting test workflow...")

    add_admin(new_admin_account)
    get_all_admins()

    remove_admin(new_admin_account)
    get_all_admins()

    for challenge in challenges:
        add_challenge(challenge)

    # Update a challenge
    updated_challenge = {
        "id": "challenge1",
        "title": "Updated Basic Flag Submission",
        "category": "Forensics",
        "description": "Updated description.",
        "flag": "updated-flag1",
        "points": 150
    }
    # update_challenge(updated_challenge)

    delete_challenge("challenge2")

    submit_flag(user1_account, "challenge1", "updated-flag1")  # Correct flag
    submit_flag(user1_account, "challenge1", "flag1")  # Wrong flag
    submit_flag(user2_account, "challenge1", "wrongflag")    # Incorrect flag

    get_solvers("challenge1")
    get_user_points(user1_account)
    get_user_points(user2_account)

    get_all_challenges()

    get_user_solves(user1_account)

    print("Test workflow completed.")

if __name__ == "__main__":
    main()
