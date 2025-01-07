# RockCTF

RockCTF is a Capture The Flag (CTF) platform that uses blockchain transactions to store challenges and user data.
The platform is built using the Flask web framework and the `web3.py` library to interact with the Ethereum blockchain, via Solidity smart contracts.

## Motivation

Traditional CTF platforms store challenges and user data in a database. This approach has several drawbacks:

- The database can be compromised, leading to data leaks.
- The platform can be taken down by a DDoS attack (see DefCamp 2024 being targeted by a Russian hacker group).
- The platform can be tampered with by an attacker.

Furthermore, there are some CTF platforms that aim to maintain full anonymity of the users/teams as the participants might be part of sensitive operations of various organizations.
This is hard to achieve as it makes the integration of a leaderboard difficult.

RockCTF uses blockchain transactions to store challenges and user data.
In turn, this allows for a tamper-proof and decentralized CTF platform, where the blockchain acts as a single source of truth, a distributed database.
Moreover, the platform maintains the anonymity of the users, as there is no PII stored, and only an address is shown publicly.
This makes it a good fit for organizations that want to host CTF competitions and maintain the privacy of the participants.

## Features

We have implemented the following features in RockCTF:

- User registration and authentication - Users employ a wallet to register and authenticate on the platform. There are two kinds of accounts: users and admins. An admin can create/delete/edit challenges. Meanwhile, a regular user can solve challenges and view the leaderboard. All user information is stored on the blockchain, users having access only to the address of the wallet, no other personal information is stored. Admin accounts need to be created locally - this is done so that, if an admin account is compromised, the attacker cannot create new admin accounts.
- Challenge creation and solving - Admins can create challenges by specifying the category, title, description, flag, and number of points for solving. Users can solve challenges by submitting the correct flag. The challenges can be of various categories (we implemented Pwn, Forensics, and OSINT), and have assigned points based on their difficulty.
- Leaderboard - Users can view the leaderboard to see the top users based on their score and compare their progress with others. Users can view the profile of others to see the challenges they have solved and their total score.
- Wallet management - Admins can fund users' wallets with Ether to allow them to participate in the CTF (outside of the webapp).

## Project Structure

```txt
├── README.md
├── backend
│   ├── contracts
│   │   └── FlagSubmission.sol
│   ├── create_admin_wallet.py
│   ├── create_wallet.py
│   ├── deploy_contract.py
│   ├── fund_user.py
│   └── test_contract.py
├── frontend
│   ├── app.py
│   ├── static
│   │   ├── icons
│   │   │   ├── admin.png
│   │   │   ├── forensics.png
│   │   │   ├── hacker.png
│   │   │   ├── logo.png
│   │   │   ├── osint.png
│   │   │   └── pwn.png
│   │   └── style.css
│   └── templates
│       ├── account.html
│       ├── add_challenge.html
│       ├── base.html
│       ├── challenge_detail.html
│       ├── challenges.html
│       ├── edit_challenge.html
│       ├── error.html
│       ├── home.html
│       ├── leaderboard.html
│       └── user_solves.html
├── package.json
└── requirements.txt
```

## Smart Contract

The smart contract `FlagSubmission.sol` is used to store the challenges and user data on the blockchain. The contract has the following functions:

- `addAdmin`: Used to promote a regular user to an admin. (transaction)
- `removeAdmin`: Used to demote an admin to a regular user. (transaction)
- `getAllAdmins`: Used to get the list of all admins. (query)
- `addChallenge`: Used to create a new challenge. (transaction)
- `updateChallenge`: Used to update an existing challenge. (transaction)
- `deleteChallenge`: Used to delete a challenge. (transaction)
- `submitFlag`: Used to submit the flag for a challenge. (transaction)
- `getSolvers`: Used to get the list of all users who solved at least one task. (query)
- `getUserPoints`: Used to get the total points of a user. (query)
- `getAllChallenges`: Used to get the list of all challenges. (query)
- `getChallengeById`: Used to get the details of a challenge by its ID. (query)
- `getUserSolves`: Used to get the list of all challenges solved by a user. (query)
- `getAllParticipants`: Used to get the list of all participants ordered by points. (query)

## Web Application

The web application is built using the Flask web framework and interacts with the smart contract using the web3.py library. The application has the following routes:

- `/` (`GET`): Home page that displays a welcome message.
- `/challenges` (`GET`): Challenges page that displays a list of all challenges. Here users can browse through the challenges and pick one to solve. They can see the title, category, and points of each challenge. As well, they can see what other users have solved the challenge.
- `/challenges/add` (`GET`, `POST`): Add challenge page that allows admins to create new challenges. Here admins can specify the category, title, description, flag, and points of the challenge.
- `/challenges/<challenge_id>`, (`GET`, `POST`): Challenge detail page that displays the details of a specific challenge. Here users can see the description and submit the flag to solve the challenge.
- `/challenges/edit/<challenge_id>` (`GET`, `POST`): Edit challenge page that allows admins to update existing challenges. Here admins can modify the category, title, description, flag, and points of the challenge.
- `/challenges/delete/<challenge_id>` (`POST`): Delete challenge page that allows admins to remove challenges. Here admins can delete the challenge.
- `/account` (`GET`, `POST`): Account page that displays the user's profile and wallet balance. Here users can see their wallet address. Additionally, users can log in by importing their wallet, or log out by deleting their session.
- `/logout` (`POST`): Logout page that allows users to log out of their account.
- `/leaderboard`, (`GET`): Leaderboard page that displays the top users based on their score. Here users can see the rank, username, and total points of each user. Their own profile is highlighted.
- `/users/<user_id>` (`GET`): User profile page that displays the details of a specific user. Here, a user can see another's solved challenges and total score.

## GitHub Repository

The source code for RockCTF is available on GitHub: [RockCTF](https://github.com/alexandra-udrescu/cockchain)

## Installation

To run RockCTF, follow these steps:

- Clone the GitHub repository: `git clone https://github.com/alexandra-udrescu/cockchain.git`
- Set up a Python virtual environment, install the required packages, and activate:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- Install the required JavaScript packages: `npm install`
- Start a local blockchain instance using Ganache: `npx ganache -d --verbose`
- Compile the Solidity smart contract:

```bash
npx solcjs --abi --bin --optimize -o ./build ./backend/contracts/FlagSubmission.sol && \
mv ./build/backend_contracts_FlagSubmission_sol_FlagSubmission.abi ./build/FlagSubmission.abi && \
mv ./build/backend_contracts_FlagSubmission_sol_FlagSubmission.bin ./build/FlagSubmission.bin
```

- Deploy the smart contract: `python backend/deploy_contract.py`
- Update the contract address in the Flask web application in `frontend/app.py`, `backend/create_admin_wallet.py`, and, if you need to, `backend/test_contract.py`
- Start the Flask web application: `python frontend/app.py`
- Access the web application in your browser at `http://localhost:5000`
- Create and fund wallets:

```bash
python backend/create_wallet.py
python backend/create_admin_wallet.py
python backend/fund_user.py  # only for users
```

## Documentation and Support

We used the following resources to build RockCTF:

- [Flask Documentation](https://flask.palletsprojects.com/en/2.0.x/)
- [web3.py Documentation](https://web3py.readthedocs.io/en/stable/)
- [Solidity Documentation](https://docs.soliditylang.org/en/v0.8.7/)
- [Ethereum Documentation](https://ethereum.org/en/developers/docs/)
- [Ganache Documentation](https://www.trufflesuite.com/docs/ganache/overview)
