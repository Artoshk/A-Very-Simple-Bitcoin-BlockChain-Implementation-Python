# Simplified BitcoinLike/BlockChain System implementation in Python with One File

A Python implementation of a blockchain system, including wallets, transactions, mining, and blockchain validation. This project demonstrates the fundamental concepts of blockchain technology.

## Features

- **Wallets**: Create and manage wallets with unique private and public keys.
- **Transactions**: Initiate transactions between wallets with support for fees.
- **Mining**: Perform proof-of-work mining to add blocks to the blockchain.
- **Validation**: Verify the integrity of the blockchain.
- **Reward System**: Reward miners for mining blocks.

## Prerequisites

- Python 3.10 or later

### Dependency Manager

This project uses [UV](https://github.com/astral-sh/uv) for managing dependencies. Make sure UV is installed:

## Installation and Running

1. Clone the repository:

   ```bash
   git clone https://github.com/Artoshk/A-Very-Simple-Bitcoin-BlockChain-Implementation-Python.git
   cd blockchain-system
   ```

2. Run UV to install dependencies:

   ```bash
   uv run main.py
   ```

## Code Overview

### Wallet Class
- Generates private and public keys for users.
- Provides methods for signing and verifying transactions.

### Transaction Class
- Represents a transaction, including sender, recipient, amount, and fees.
- Includes methods for validation and signing.

### Block Class
- Represents a block containing transactions, a nonce, and the hash of the previous block.
- Includes a mining method for proof-of-work.

### Blockchain Class
- Manages the chain of blocks.
- Validates the integrity of the chain.
- Handles mining rewards and wallet balances.

### Pool Class
- Maintains a pool of pending transactions.
- Supports adding and clearing transactions.

## Example Usage

### Wallet Creation

```python
alice_wallet = Wallet("Alice")
bob_wallet = Wallet("Bob")
print("Alice's Public Key:", alice_wallet.public_key)
```

### Adding Transactions

```python
transaction = Transaction(alice_wallet, bob_wallet.public_key, 10)
transaction_pool.add_transaction(transaction, alice_wallet)
```

### Mining Blocks

```python
await blockchain.add_block(transaction_pool.get_transactions(), [miner_wallet])
transaction_pool.clear_transactions()
```

## Testing

To test the implementation, simply run the `main.py` script and observe the outputs for:

- Wallet balances after mining and transactions.
- Blockchain structure and validation.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Built using the [UV](https://github.com/astral-sh/uv) dependency manager.
- Cryptographic functionality provided by the `cryptography` library.
