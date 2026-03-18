# aa-py

**aa-py** is a production-grade Python SDK for Ethereum Account Abstraction, specifically designed for **EntryPoint v0.9**, **EIP-7702**, and **ERC-7677**.

## Features

- **EntryPoint v0.9 Support**: Optimized for the latest AA standards including 128-bit gas packing.
- **EIP-7702 Integration**: Build Type-4 transactions to delegate EOA accounts to smart account logic.
- **ERC-7677 Paymaster**: Standardized interface for `pm_getPaymasterStubData` and `pm_getPaymasterAndData`.
- **2D Nonce Management**: Built-in support for parallel transaction execution via 2D nonces.
- **Developer-Centric API**: Send complex AA transactions with a single method call using `SmartAccount`.

## Installation

```bash
pip install .
```

## Quick Start (AA Transaction)

```python
from aa_py.account import SmartAccount
from aa_py.signer import UserOpSigner
from aa_py.provider import BundlerProvider

# Initialize components
signer = UserOpSigner(PRIVATE_KEY)
provider = BundlerProvider(RPC_URL, ENTRY_POINT)

# Create SmartAccount
account = SmartAccount(
    address=ACCOUNT_ADDRESS,
    signer=signer,
    provider=provider,
    entry_point=ENTRY_POINT,
    chain_id=1
)

# Send transaction
op_hash = account.send_transaction(to="0x...", data="0x", value=0)
print(f"UserOp Hash: {op_hash}")
```

## EIP-7702 Delegation

```python
from aa_py.eip7702 import Authorization, EIP7702Transaction

# Create and sign authorization
auth = Authorization(chain_id=1, address=SMART_ACCOUNT_LOGIC, nonce=0)
auth.sign(EOA_PRIVATE_KEY)

# Build Type-4 transaction
tx = EIP7702Transaction(tx_data, [auth]).prepare()
# Now send 'tx' via standard web3.py
```

## License

MIT
