from flask import Flask, render_template, request, redirect, url_for, make_response, flash
import json
from web3 import Web3
import os

app = Flask(__name__)
app.secret_key = "your_random_generated_secret_key"

web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
if not web3.is_connected():
    raise Exception("Failed to connect to the blockchain. Make sure Ganache is running.")

with open("build/FlagSubmission.abi", "r") as abi_file:
    contract_abi = json.load(abi_file)

contract_address = "0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab"  # Replace with your deployed contract address
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def get_challenges():
    challenges = []
    try:
        contract_challenges = contract.functions.getAllChallenges().call()
        for ch in contract_challenges:
            challenges.append({
                "id": ch[0],
                "title": ch[1],
                "category": ch[2],
                "description": ch[3],
                "points": ch[5],
                "icon": f"{ch[2].lower()}.png"
            })
    except Exception as e:
        print(f"Error fetching challenges: {e}")
    return challenges

def get_leaderboard():
    leaderboard = []
    try:
        participants = contract.functions.getAllParticipants().call()
        
        for user in participants:
            points = contract.functions.getUserPoints(user).call()
            leaderboard.append({"username": user, "points": points})
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
    return sorted(leaderboard, key=lambda x: x["points"], reverse=True)

def get_challenge_by_id(challenge_id):
    try:
        challenge_data = contract.functions.getChallengeById(challenge_id).call()
        challenge = {
            "id": challenge_data[0],
            "title": challenge_data[1],
            "category": challenge_data[2],
            "description": challenge_data[3],
            "points": challenge_data[4],
            "solvers": challenge_data[5],
            "icon": f"{challenge_data[2].lower()}.png"
        }
        return challenge
    except Exception as e:
        print(f"Error fetching challenge {challenge_id}: {e}")
        return None

def get_user_solves(user_id):
    solves = []
    try:
        contract_solves = contract.functions.getUserSolves(user_id).call()
        for solve in contract_solves:
            solves.append({
                "id": solve[0],
                "title": solve[1],
                "category": solve[2],
                "points": solve[5],
            })
    except Exception as e:
        print(f"Error fetching solves for {user_id}: {e}")
    return solves

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/account", methods=["GET", "POST"])
def account():
    address = request.cookies.get("address", "Not Set")
    is_admin = False

    try:
        admin_list = contract.functions.getAllAdmins().call()
        if address != "Not Set" and Web3.is_address(address):
            is_admin = Web3.to_checksum_address(address) in [Web3.to_checksum_address(admin) for admin in admin_list]

    except Exception as e:
        print(f"Error fetching admin list: {e}")
        is_admin = False

    if request.method == "POST":
        wallet_file = request.files.get("wallet_file")
        if wallet_file:
            try:
                wallet_data = json.load(wallet_file)
                address = wallet_data.get("address", "Not Set")
                private_key = wallet_data.get("private_key", "Not Set")

                if not Web3.is_address(address):
                    raise ValueError("Invalid Ethereum address in wallet file.")

                if not os.path.exists("wallets"):
                    os.makedirs("wallets")
                wallet_path = f"wallets/{address}.json"
                if not os.path.exists(wallet_path):
                    with open(wallet_path, "w") as f:
                        json.dump(wallet_data, f, indent=4)

                admin_list = contract.functions.getAllAdmins().call()
                is_admin = Web3.to_checksum_address(address) in [Web3.to_checksum_address(admin) for admin in admin_list]

                resp = make_response(redirect(url_for("account")))
                resp.set_cookie("address", address)
                resp.set_cookie("private_key", private_key)
                return resp

            except Exception as e:
                return render_template("account.html", error=f"Invalid wallet file: {str(e)}")

    return render_template(
        "account.html",
        address=address,
        is_admin=is_admin,
    )

@app.route("/challenges", methods=["GET"])
def challenges_list():
    challenges = get_challenges()
    address = request.cookies.get("address", "Not Set")
    is_admin = False

    try:
        admin_list = contract.functions.getAllAdmins().call()
        if address != "Not Set" and Web3.is_address(address):
            is_admin = Web3.to_checksum_address(address) in [Web3.to_checksum_address(admin) for admin in admin_list]

    except Exception as e:
        print(f"Error checking admin status: {e}")

    return render_template("challenges.html", challenges=challenges, is_admin=is_admin)

@app.route("/challenges/add", methods=["GET", "POST"])
def add_challenge():
    address = request.cookies.get("address", "Not Set")
    private_key = request.cookies.get("private_key", "Not Set")
    is_admin = False

    try:
        admin_list = contract.functions.getAllAdmins().call()
        if address != "Not Set" and Web3.is_address(address):
            is_admin = Web3.to_checksum_address(address) in [Web3.to_checksum_address(admin) for admin in admin_list]
    except Exception as e:
        flash(f"Error checking admin status: {e}", "error")

    if not is_admin:
        flash("You do not have permission to add challenges.", "error")
        return redirect(url_for("challenges_list"))

    try:
        contract_challenges = contract.functions.getAllChallenges().call()
        if contract_challenges:
            last_challenge_id = contract_challenges[-1][0]
            new_id_number = int(last_challenge_id.replace("challenge", "")) + 1
            new_challenge_id = f"challenge{new_id_number}"
        else:
            new_challenge_id = "challenge1"

    except Exception as e:
        flash(f"Error computing new challenge ID: {e}", "error")
        new_challenge_id = "challenge1"

    if request.method == "POST":
        try:
            title = request.form.get("title")
            category = request.form.get("category")
            description = request.form.get("description")
            flag = request.form.get("flag")
            points = int(request.form.get("points"))

            tx = contract.functions.addChallenge(
                new_challenge_id,
                title,
                category,
                description,
                flag,
                points
            ).build_transaction({
                'from': address,
                'nonce': web3.eth.get_transaction_count(address),
                'gas': 5000000,
                'gasPrice': web3.to_wei('20', 'gwei')
            })

            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            web3.eth.wait_for_transaction_receipt(tx_hash)

            flash("Challenge added successfully!", "success")
            return redirect(url_for("challenges_list"))

        except Exception as e:
            print(e)
            flash(f"Error adding challenge: {e}", "error")
    
    return render_template("add_challenge.html", new_challenge_id=new_challenge_id)

@app.route("/challenges/edit/<challenge_id>", methods=["GET", "POST"])
def edit_challenge(challenge_id):
    address = request.cookies.get("address", "Not Set")
    private_key = request.cookies.get("private_key", "Not Set")
    is_admin = False

    try:
        admin_list = contract.functions.getAllAdmins().call()
        if address != "Not Set" and Web3.is_address(address):
            is_admin = Web3.to_checksum_address(address) in [Web3.to_checksum_address(admin) for admin in admin_list]

    except Exception as e:
        print(f"Error checking admin status: {e}")

    if not is_admin:
        flash("You do not have permission to edit challenges.", "error")
        return redirect(url_for("challenges_list"))

    challenge = get_challenge_by_id(challenge_id)

    if request.method == "POST":
        try:
            title = request.form.get("title")
            category = request.form.get("category")
            description = request.form.get("description")
            flag = request.form.get("flag")
            points = int(request.form.get("points"))

            tx = contract.functions.updateChallenge(
                challenge_id, title, category, description, flag, points
            ).build_transaction({
                'from': address,
                'nonce': web3.eth.get_transaction_count(address),
                'gas': 5000000,
                'gasPrice': web3.to_wei('20', 'gwei')
            })

            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            web3.eth.wait_for_transaction_receipt(tx_hash)

            flash("Challenge updated successfully!", "success")
            return redirect(url_for("challenges_list"))

        except Exception as e:
            flash(f"Error updating challenge: {e}", "error")

    return render_template("edit_challenge.html", challenge=challenge)


@app.route("/challenges/delete/<challenge_id>", methods=["POST"])
def delete_challenge(challenge_id):
    address = request.cookies.get("address", "Not Set")
    private_key = request.cookies.get("private_key", "Not Set")
    is_admin = False

    try:
        admin_list = contract.functions.getAllAdmins().call()
        if address != "Not Set" and Web3.is_address(address):
            is_admin = Web3.to_checksum_address(address) in [Web3.to_checksum_address(admin) for admin in admin_list]

    except Exception as e:
        print(f"Error checking admin status: {e}")

    if not is_admin:
        flash("You do not have permission to delete challenges.", "error")
        return redirect(url_for("challenges_list"))

    try:
        tx = contract.functions.deleteChallenge(challenge_id).build_transaction({
            'from': address,
            'nonce': web3.eth.get_transaction_count(address),
            'gas': 5000000,
            'gasPrice': web3.to_wei('20', 'gwei')
        })

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        web3.eth.wait_for_transaction_receipt(tx_hash)

        flash("Challenge deleted successfully!", "success")

    except Exception as e:
        flash(f"Error deleting challenge: {e}", "error")

    return redirect(url_for("challenges_list"))

@app.route("/leaderboard")
def leaderboard():
    leaderboard = get_leaderboard()
    return render_template("leaderboard.html", users=leaderboard, address=request.cookies.get("address"))

@app.route("/challenges/<challenge_id>", methods=["GET", "POST"])
def challenge(challenge_id):
    address = request.cookies.get("address")
    private_key = request.cookies.get("private_key")
    challenge_data = None 
    solvers = []
    
    try:
        challenge_data = contract.functions.getChallengeById(challenge_id).call()
        solvers = contract.functions.getSolvers(challenge_id).call()
    except Exception as e:
        flash(f"Error fetching challenge: {str(e)}", "error")
        return redirect(url_for("challenges"))

    if request.method == "POST":
        flag = request.form.get("flag", "").strip()
        
        if not address or not private_key:
            flash("You need to authenticate first. Go to the 'Account' page.", "error")
            return redirect(url_for("challenge", challenge_id=challenge_id))
            
        if not flag:
            flash("Flag cannot be empty.", "error")
            return redirect(url_for("challenge", challenge_id=challenge_id))
            
        try:
            txn = contract.functions.submitFlag(challenge_id, flag).build_transaction({
                'from': address,
                'nonce': web3.eth.get_transaction_count(address),
                'gas': 5000000,
                'gasPrice':  web3.to_wei("20", "gwei"),
            })
            
            signed_txn = web3.eth.account.sign_transaction(txn, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                flash("Flag correct! You have solved the challenge.", "success")
            else:
                flash(f"Incorrect flag!", "error")
                
        except ValueError as ve:
            flash(f"Transaction error: {str(ve)}", "error")
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for("challenge", challenge_id=challenge_id))

    return render_template(
        "challenge_detail.html",
        challenge=challenge_data,
        solvers=solvers,
        address=request.cookies.get("address"),
    )

@app.route("/logout", methods=["POST"])
def logout():
    resp = make_response(redirect(url_for("account")))
    resp.delete_cookie("address")
    resp.delete_cookie("private_key")
    flash("You have been logged out successfully.", "info")
    return resp

@app.route("/users/<user_id>")
def user_solves(user_id):
    solves = get_user_solves(user_id)
    return render_template("user_solves.html", user_id=user_id, solves=solves)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", message="Page not found"), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
