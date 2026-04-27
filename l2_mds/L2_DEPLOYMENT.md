# L2 Deployment Guide for SynthShield Forensic Anchoring

## Overview

SynthShield now includes integrated Ethereum L2 support for daily Merkle root anchoring. This ensures immutability and regulatory compliance (S.3741) for synthesizer audit trails.

## Architecture

```
[Synthesis Events]
        ↓
    [Black Box Chain] ← Cryptographic hashing & HMAC chaining
        ↓
    [Daily Merkle Root] ← Binary tree aggregation
        ↓
    [EthereumAnchor] ← Web3 L2 submission
        ↓
[ForensicAnchor.sol] ← Smart contract on Optimism/Arbitrum/Base
```

## Supported L2 Networks

- **Optimism** (mainnet.optimism.io)
- **Arbitrum** (arb1.arbitrum.io)
- **Base** (mainnet.base.org)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Deploy Smart Contract

#### Option A: Using Foundry (Recommended)

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Initialize project
forge init synthshield-anchor
cd synthshield-anchor

# Copy contract
cp ../synthshield/contracts/ForensicAnchor.sol src/

# Compile
forge build

# Deploy to Optimism
export DEPLOYER_KEY=0x...  # Your private key (hex)
export RPC_URL=https://mainnet.optimism.io
export ETHERSCAN_API_KEY=...  # For verification

forge create src/ForensicAnchor.sol:ForensicAnchor \
  --rpc-url $RPC_URL \
  --private-key $DEPLOYER_KEY \
  --verify \
  --verifier etherscan \
  --etherscan-api-key $ETHERSCAN_API_KEY
```

#### Option B: Using Hardhat

```bash
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npx hardhat init

# Update hardhat.config.js for Optimism
# Deploy using Hardhat scripts
npx hardhat run scripts/deploy.js --network optimism
```

### 3. Configure Environment Variables

Create a `.env` file:

```bash
# L2 Configuration
L2_NETWORK=optimism
L2_RPC_URL=https://mainnet.optimism.io
L2_CONTRACT_ADDRESS=0x...  # Deployed contract address

# Wallet Private Key
L2_PRIVATE_KEY=your_private_key_here  # Without 0x prefix

# Hardware Configuration
L2_HARDWARE_ID=TPM-SYNTH-001  # Unique device ID
```

## Usage

### Example 1: Mock L2 Mode (No Network Required)

```python
from synthshield.core.forensic_orchestrator import ForensicOrchestrator
import torch

# Initialize orchestrator with mock L2
orchestrator = ForensicOrchestrator(
    hardware_id="SYNTH-DEMO-001",
    tpm_secret=b"root_of_trust_secret_12345",
    use_mock_l2=True,  # Mock mode
    sentinel_head=sentinel_head_model,
    screening_threshold=0.5
)

# Log synthesis events
result = orchestrator.log_synthesis_event(
    synthesis_id="SYN-0001",
    sequence="MKTAYIAKQRQISFVKSHFSRQDILDLWQ",
    embeddings=torch.randn(1, 1280),  # ESM-2 embeddings
    status="success"
)

# Generate daily proof
merkle_root = orchestrator.generate_daily_merkle_root()

# Submit to L2 (mock)
submission = orchestrator.submit_daily_anchor_to_l2(
    data_url="ipfs://bafkyabc123"
)

# Print audit summary
orchestrator.print_audit_summary()

# Export audit log for compliance
orchestrator.export_audit_log_json("audit_log.json")
```

### Example 2: Live L2 Mode (Optimism)

```python
from synthshield.core.forensic_orchestrator import ForensicOrchestrator
import os

# Configure L2
l2_config = {
    "contract_address": os.getenv("L2_CONTRACT_ADDRESS"),
    "rpc_url": os.getenv("L2_RPC_URL"),
    "private_key": os.getenv("L2_PRIVATE_KEY"),
    "network": "optimism"
}

# Initialize orchestrator with live L2
orchestrator = ForensicOrchestrator(
    hardware_id=os.getenv("L2_HARDWARE_ID"),
    tpm_secret=b"hardware_root_of_trust",
    use_mock_l2=False,
    l2_config=l2_config,
    sentinel_head=sentinel_head_model,
    screening_threshold=0.5
)

# Log events throughout the day
for event_data in today_synthesis_events:
    orchestrator.log_synthesis_event(
        synthesis_id=event_data['id'],
        sequence=event_data['sequence'],
        embeddings=get_embeddings(event_data['sequence']),
        status=event_data['status']
    )

# At end of day: submit to L2
submission = orchestrator.submit_daily_anchor_to_l2()

print(f"Anchor TX: {submission['tx_hash']}")
print(f"Block: {submission['block_number']}")
```

### Example 3: Direct Ethereum Anchor

```python
from synthshield.web.ethereum_anchor import EthereumAnchor

# Initialize anchor client
anchor = EthereumAnchor(
    contract_address="0x...",
    rpc_url="https://mainnet.optimism.io",
    private_key="0x...",
    hardware_id="TPM-SYNTH-001",
    network="optimism"
)

# Submit a Merkle root
result = anchor.submit_merkle_root(
    merkle_root_hex="0xabcd1234...",
    data_url="ipfs://bafkyabc123",
    simulate=False,
    wait_for_receipt=True
)

# Verify on-chain
is_verified = anchor.verify_anchor_on_chain(
    synthesizer_address="0x...",
    merkle_root_hex="0xabcd1234..."
)

print(f"On-chain verification: {is_verified}")
```

## Contract Functions

### Submitting Anchors

```solidity
function submitAnchor(
    bytes32 merkleRoot,
    string calldata hardwareId,
    string calldata dataUrl
) public onlyAuthorized
```

- **merkleRoot**: 32-byte root hash of daily synthesis events
- **hardwareId**: TPM serial or secure enclave ID
- **dataUrl**: IPFS hash for retrieving full logs

### Verification

```solidity
function verifyAnchor(
    address synthesizer,
    bytes32 merkleRoot
) public view returns (bool)
```

Returns true if the root is anchored for the synthesizer.

### Admin Functions

```solidity
function authorizeSynthesizer(address synthesizer) public onlyOwner
function revokeSynthesizer(address synthesizer) public onlyOwner
function verifyAnchorManual(bytes32 merkleRoot) public onlyOwner
```

## Gas Costs

| Network | Avg Gas | Est. Cost (USD) |
|---------|--------|-----------------|
| Optimism | 50,000 - 100,000 | $0.01 - $0.05 |
| Arbitrum | 50,000 - 100,000 | $0.01 - $0.03 |
| Base | 50,000 - 100,000 | $0.01 - $0.05 |

## Audit Trail Flow

1. **Event Logging** → Black Box chain logs each synthesis event
2. **Chain Verification** → Verify no tampering via hash chain
3. **Merkle Aggregation** → Generate root of daily events
4. **L2 Submission** → Send root + timestamp to smart contract
5. **Immutable Record** → Root is permanently anchored on-chain
6. **IPFS Backup** → Full logs stored on IPFS for off-chain access

## S.3741 Compliance

SynthShield satisfies the Biosecurity Modernization Act by:

✓ **Logging**: Every synthesis event is cryptographically logged  
✓ **Chaining**: Events are HMAC-linked with hardware RoT secret  
✓ **Anchoring**: Daily Merkle roots are anchored to public L2 ledger  
✓ **Immutability**: On-chain anchors prove logs haven't been altered  
✓ **Auditability**: Full logs references via IPFS for third-party verification  

## Troubleshooting

### Issue: Connection Failed to L2

```
Error: Failed to connect to optimism at https://mainnet.optimism.io
```

**Solution**:
- Check RPC URL is correct
- Verify network connectivity
- Try alternative RPC endpoints (e.g., Infura, Alchemy)

### Issue: Transaction Failed (Insufficient Gas)

```
Error: gas required exceeds allowance
```

**Solution**:
- Increase gas limit in contract calls (currently set to 150,000)
- Ensure wallet has sufficient ETH on L2

### Issue: Synthesizer Not Authorized

```
Error: Synthesizer not authorized
```

**Solution**:
- Call `authorizeSynthesizer(wallet_address)` from contract owner
- Verify contract is deployed on correct L2 network

## Security Considerations

1. **Private Key Management**:
   - Use environment variables or secure vaults (never hardcode)
   - Rotate keys periodically
   - Use hardware wallets for production

2. **TPM Integration**:
   - For production, integrate with actual TPM/secure enclave
   - Current implementation uses in-memory secret (demo only)

3. **Contract Auditing**:
   - Have ForensicAnchor.sol audited by security firm
   - Test on testnet before mainnet deployment

4. **IPFS Storage**:
   - Ensure logs are pinned to prevent removal
   - Use multiple IPFS nodes for redundancy

## References

- [S.3741 Biosecurity Modernization Act](https://www.congress.gov/bill/117th-congress/senate-bill/3741)
- [Optimism Documentation](https://docs.optimism.io)
- [Arbitrum Documentation](https://docs.arbitrum.io)
- [Solidity Documentation](https://docs.soliditylang.org)
