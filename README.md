# Project Description

This project is a CTF (Capture The Flag) platform that integrates a blockchain-based smart contract for managing challenges, user submissions, and leaderboard tracking. It includes:

- **Smart Contract:** Handles challenge creation, flag submissions, and score updates.
- **Web Application:** Provides a GUI for users to interact with the platform.
- **Wallet Management:** Supports Ethereum wallets for secure flag submission.
- **Local Blockchain:** Uses Ganache for testing and development.

---

# Project Setup and Usage

This guide provides step-by-step instructions to set up and use the project.

## **Setup**

### 1. Install Node.js Dependencies
```bash
npm install
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## **Running the Local Blockchain**

Start a local blockchain instance using Ganache:
```bash
npx ganache -d --verbose
```

---

## **Compiling the Smart Contract**

Compile the Solidity smart contract and move the generated ABI and binary files:
```bash
npx solcjs --abi --bin --optimize -o ./build ./backend/contracts/FlagSubmission.sol && \
mv ./build/backend_contracts_FlagSubmission_sol_FlagSubmission.abi ./build/FlagSubmission.abi && \
mv ./build/backend_contracts_FlagSubmission_sol_FlagSubmission.bin ./build/FlagSubmission.bin
```

---

## **Deploying the Smart Contract**

Deploy the compiled smart contract to the local blockchain:
```bash
python backend/deploy_contract.py
```

---

## **Testing the Smart Contract**

Run the test script to interact with the smart contract. Note: This uses unlocked accounts.
```bash
python backend/test_contract.py
```

---

## **Wallet Management**

### Create a Wallet
Generate a new wallet file:
```bash
python create_wallet.py
```

### Add Funds to a Wallet
Transfer funds to the wallet:
```bash
python fund_user.py
```

---

## **Running the Web Application**

Start the web application:
```bash
python frontend/app.py
```

---

## **Icons**

Icons for the application can be downloaded from:
[Flaticon](https://www.flaticon.com/)

---
