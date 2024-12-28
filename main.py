import hashlib
import json
import time
import asyncio
from typing import List
import random
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature, decode_dss_signature

# Wallet
class Wallet:
    def __init__(self, name: str):
        self.name = name
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()
        self.balance = 0.0

    def sign_transaction(self, data: str):
        signature = self.private_key.sign(
            data.encode(),
            ec.ECDSA(hashes.SHA256())
        )
        return encode_dss_signature(*decode_dss_signature(signature))

    def verify_signature(self, data: str, signature):
        try:
            self.public_key.verify(
                signature,
                data.encode(),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False

# Transaction
class Transaction:
    def __init__(self, sender_wallet: Wallet, recipient_public_key, amount: float):
        self.sender_public_key = sender_wallet.public_key
        self.recipient = recipient_public_key
        self.amount = amount
        self.fee = round(0.005 * amount, 8)  # Fee is 0.5% of transaction value
        self.timestamp = time.time()
        self.signature = self.sign_transaction(sender_wallet)

    def to_dict(self):
        return json.dumps({
            "sender_public_key": self.sender_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode(),
            "recipient": self.recipient.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode(),
            "amount": self.amount,
            "fee": self.fee,
            "timestamp": self.timestamp,
        }, indent=4)

    def calculate_hash(self):
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()

    def sign_transaction(self, sender_wallet: Wallet):
        data = json.dumps(self.to_dict(), sort_keys=True)
        return sender_wallet.sign_transaction(data)

    def is_valid(self, sender_wallet: Wallet):
        data = json.dumps(self.to_dict(), sort_keys=True)
        return sender_wallet.verify_signature(data, self.signature)

# Block
class Block:
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, difficulty: int, miner):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.difficulty = difficulty
        self.miner = miner
        self.hash = None

    def calculate_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "miner": self.miner.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode() if self.miner else "GENESIS_BLOCK",
        }
        return hashlib.sha256(json.dumps(block_data, sort_keys=True).encode()).hexdigest()


    async def mine_block(self):
        prefix = "0" * self.difficulty
        while True:
            self.hash = self.calculate_hash()
            if self.hash.startswith(prefix):
                return self.hash
            self.nonce += 1

# Blockchain
class Blockchain:
    def __init__(self, difficulty: int = 4, reward: float = 50.0):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.reward = reward
        self.wallets = {}

    async def initialize(self):
        await self.create_genesis_block()

    async def create_genesis_block(self):
        genesis_block = Block(0, [], "0", self.difficulty, None)
        await genesis_block.mine_block()
        self.chain.append(genesis_block)

    def find_wallet_by_public_key(self, public_key):
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        return self.wallets.get(public_key_pem)

    async def add_block(self, transactions: List[Transaction], miner_wallets: List[Wallet]):
        previous_hash = self.chain[-1].hash
        miner = random.choice(miner_wallets)
        total_fees = sum(transaction.fee for transaction in transactions if transaction.is_valid(self.find_wallet_by_public_key(transaction.sender_public_key)))
        new_block = Block(len(self.chain), transactions, previous_hash, self.difficulty, miner.public_key)
        await new_block.mine_block()
        self.chain.append(new_block)
        miner.balance += self.reward + total_fees

        # Update balances
        for transaction in transactions:
            if transaction.is_valid(self.find_wallet_by_public_key(transaction.sender_public_key)):
                sender_wallet = self.find_wallet_by_public_key(transaction.sender_public_key)
                recipient_wallet = self.find_wallet_by_public_key(transaction.recipient)

                if sender_wallet:
                    sender_wallet.balance -= transaction.amount + transaction.fee
                if recipient_wallet:
                    recipient_wallet.balance += transaction.amount

    def register_wallet(self, wallet: Wallet):
        public_key_pem = wallet.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        self.wallets[public_key_pem] = wallet

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

# Pool
class Pool:
    def __init__(self):
        self.transactions: List[Transaction] = []

    def add_transaction(self, transaction: Transaction, sender_wallet: Wallet):
        if transaction.amount > 0 and transaction.sender_public_key != transaction.recipient:
            if sender_wallet.balance >= transaction.amount + transaction.fee:
                self.transactions.append(transaction)

    def get_transactions(self):
        return self.transactions

    def clear_transactions(self):
        self.transactions = []

async def main():
    # Create wallets
    alice_wallet = Wallet("Alice")
    bob_wallet = Wallet("Bob")
    charlie_wallet = Wallet("Charlie")

    wallets = [alice_wallet, bob_wallet, charlie_wallet]

    # Register wallets in blockchain
    blockchain = Blockchain()
    await blockchain.initialize()

    for wallet in wallets:
        blockchain.register_wallet(wallet)

    alice_address = alice_wallet.public_key
    bob_address = bob_wallet.public_key
    charlie_address = charlie_wallet.public_key

    print(f"Alice's Address: \n{alice_address.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()}")
    print(f"Bob's Address: \n{bob_address.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()}")
    print(f"Charlie's Address: \n{charlie_address.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()}")

    # Create a transaction pool
    pool = Pool()

    # Mine the first block to reward a miner
    await blockchain.add_block(pool.get_transactions(), [alice_wallet])
    pool.clear_transactions()

    # Check balances after mining
    print("Balances after first mining:")
    for wallet in wallets:
        print(f"{wallet.name}: {wallet.balance}")

    # Create and add a transaction
    transaction1 = Transaction(alice_wallet, bob_wallet.public_key, 10)
    pool.add_transaction(transaction1, alice_wallet)
    print("Transaction added to pool:", transaction1.to_dict())

    # Add another block
    await blockchain.add_block(pool.get_transactions(), [charlie_wallet])  # One random wallet will receive the reward. If you want someone specific to mine like charlie, just change to [charlie_wallet]
    pool.clear_transactions()

    # Check balances after transaction and mining
    print("Balances after second block:")
    for wallet in wallets:
        print(f"{wallet.name}: {wallet.balance}")

    print("\nBlockchain valid:", blockchain.is_chain_valid())
    print("\nBlockchain:")
    for block in blockchain.chain:
        print(json.dumps({
            "index": block.index,
            "transactions": [tx.to_dict() for tx in block.transactions],
            "previous_hash": block.previous_hash,
            "hash": block.hash,
            "miner": block.miner.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode() if block.miner else "GENESIS_BLOCK",
        }, indent=4))

if __name__ == "__main__":
    asyncio.run(main())  # Run the async main function