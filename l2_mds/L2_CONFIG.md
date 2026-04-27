# L2 Configuration Template for SynthShield

## Environment Variables (.env)

Copy this template to `.env` at the project root and fill in your values:

```bash
# ============================================
# L2 ETHEREUM CONFIGURATION
# ============================================

# Network selection: optimism, arbitrum, base
L2_NETWORK=optimism

# RPC Endpoint (use your provider's URL)
# Optimism:  https://mainnet.optimism.io
# Arbitrum:  https://arb1.arbitrum.io  
# Base:      https://mainnet.base.org
L2_RPC_URL=https://mainnet.optimism.io

# Deployed ForensicAnchor contract address (from deployment)
# Format: 0x[40 hex characters]
L2_CONTRACT_ADDRESS=0x...

# Wallet private key (NEVER commit this to version control!)
# Format: hex string WITHOUT 0x prefix, or with 0x prefix
# Example: abc123def456... or 0xabc123def456...
L2_PRIVATE_KEY=

# Hardware identifier (unique to your synthesizer)
# Examples: TPM-SYNTH-001, ENCLAVE-LAB-A, DEVICE-SN-12345
L2_HARDWARE_ID=

# ============================================
# OPTIONAL: IPFS CONFIGURATION
# ============================================

# IPFS gateway for log storage (optional)
# Examples: https://ipfs.io, https://dweb.link, local node
IPFS_GATEWAY=https://ipfs.io

# IPFS API endpoint (if using local IPFS node)
IPFS_API_URL=http://localhost:5001

# ============================================
# OPTIONAL: BACKUP CONFIGURATION
# ============================================

# Backup L2 networks (for redundancy)
L2_BACKUP_NETWORKS=arbitrum,base

# Alternative RPC endpoints
L2_BACKUP_RPC_URLS=https://arb1.arbitrum.io,https://mainnet.base.org

# ============================================
# DEPLOYMENT NOTES
# ============================================

# After setting these values:
# 1. Deploy ForensicAnchor.sol to your chosen L2
# 2. Copy the contract address to L2_CONTRACT_ADDRESS
# 3. Fund the wallet with some ETH on the L2
# 4. Ensure wallet is authorized by contract owner:
#    contract.authorizeSynthesizer(wallet_address)
# 5. Test with mock mode first:
#    ForensicOrchestrator(..., use_mock_l2=True, ...)
# 6. Then switch to live mode with these env vars
```

## Python Usage

### Load from .env file

```python
from dotenv import load_dotenv
import os
from synthshield.core.forensic_orchestrator import ForensicOrchestrator

# Load environment variables
load_dotenv()

# Create L2 config from env
l2_config = {
    "contract_address": os.getenv("L2_CONTRACT_ADDRESS"),
    "rpc_url": os.getenv("L2_RPC_URL"),
    "private_key": os.getenv("L2_PRIVATE_KEY"),
    "network": os.getenv("L2_NETWORK", "optimism")
}

# Initialize orchestrator with live L2
orchestrator = ForensicOrchestrator(
    hardware_id=os.getenv("L2_HARDWARE_ID"),
    tpm_secret=b"your_root_of_trust_secret",
    use_mock_l2=False,
    l2_config=l2_config
)
```

### Configuration Dictionary

```python
# Minimal configuration
l2_config = {
    "contract_address": "0x...",
    "rpc_url": "https://mainnet.optimism.io",
    "private_key": "0x...",
    "network": "optimism"
}

# Full configuration with backups
l2_config = {
    "contract_address": "0x...",
    "rpc_url": "https://mainnet.optimism.io",
    "private_key": "0x...",
    "network": "optimism",
    
    # Optional: Backup L2s for failover
    "backup_networks": [
        {
            "rpc_url": "https://arb1.arbitrum.io",
            "contract_address": "0x...",
            "network": "arbitrum"
        },
        {
            "rpc_url": "https://mainnet.base.org",
            "contract_address": "0x...",
            "network": "base"
        }
    ]
}
```

## Deployment Checklist

- [ ] Solidity contract compiled (ForensicAnchor.sol)
- [ ] Contract deployed to L2 network
- [ ] Contract address recorded
- [ ] Wallet funded with ETH on L2 (for gas)
- [ ] Wallet authorized by contract owner
- [ ] .env file created with configuration
- [ ] Tested with mock L2 mode first
- [ ] Tested with live L2 on testnet
- [ ] Tested Merkle root submission
- [ ] Tested on-chain verification
- [ ] Audit log export tested
- [ ] Ready for mainnet deployment

## Testing Configuration

```python
# Test with mock L2 (no network required)
from synthshield.core.forensic_orchestrator import ForensicOrchestrator

orchestrator = ForensicOrchestrator(
    hardware_id="TEST-SYNTH-001",
    tpm_secret=b"test_root_secret",
    use_mock_l2=True,  # Mock mode - no network
    sentinel_head=None
)

# Test with testnet L2
orchestrator = ForensicOrchestrator(
    hardware_id="TESTNET-SYNTH-001",
    tpm_secret=b"testnet_root_secret",
    use_mock_l2=False,
    l2_config={
        "contract_address": "0x...",
        "rpc_url": "https://sepolia.optimism.io",  # Optimism testnet
        "private_key": "0x...",
        "network": "optimism-sepolia"
    }
)
```

## Security Best Practices

1. **Never commit .env to git**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use different wallets for different networks**
   - Testnet: Test wallet with limited funds
   - Mainnet: Production wallet with vault/HSM

3. **Rotate private keys periodically**
   - Generate new wallet
   - Migrate to new contract
   - Revoke old wallet

4. **Validate RPC endpoints**
   - Test connectivity before deployment
   - Use reputable providers (Optimism, Alchemy, Infura)
   - Implement fallback endpoints

5. **Monitor L2 costs**
   - Optimism: ~$0.01-0.05 per anchor
   - Arbitrum: ~$0.01-0.03 per anchor
   - Base: ~$0.01-0.05 per anchor

## Troubleshooting Configuration Issues

### Issue: "Invalid contract address"
```python
# Ensure correct format
contract_address = "0x" + contract_address if not contract_address.startswith("0x") else contract_address
contract_address = Web3.to_checksum_address(contract_address)
```

### Issue: "Failed to connect to RPC"
```python
# Test RPC connectivity
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("YOUR_RPC_URL"))
print(w3.is_connected())  # Should print True
```

### Issue: "Insufficient funds"
```bash
# Check wallet balance
# Fund wallet with ETH on L2
# Typical cost: 50,000 - 100,000 gas @ current price
```

## Reference: Network Configurations

### Optimism Mainnet
```python
{
    "network": "optimism",
    "rpc_url": "https://mainnet.optimism.io",
    "chain_id": 10,
    "explorer": "https://optimistic.etherscan.io"
}
```

### Optimism Sepolia (Testnet)
```python
{
    "network": "optimism-sepolia",
    "rpc_url": "https://sepolia.optimism.io",
    "chain_id": 11155420,
    "explorer": "https://sepolia-optimism.etherscan.io"
}
```

### Arbitrum Mainnet
```python
{
    "network": "arbitrum",
    "rpc_url": "https://arb1.arbitrum.io/rpc",
    "chain_id": 42161,
    "explorer": "https://arbiscan.io"
}
```

### Arbitrum Sepolia (Testnet)
```python
{
    "network": "arbitrum-sepolia",
    "rpc_url": "https://sepolia-rollup.arbitrum.io/rpc",
    "chain_id": 421614,
    "explorer": "https://sepolia.arbiscan.io"
}
```

### Base Mainnet
```python
{
    "network": "base",
    "rpc_url": "https://mainnet.base.org",
    "chain_id": 8453,
    "explorer": "https://basescan.org"
}
```

### Base Sepolia (Testnet)
```python
{
    "network": "base-sepolia",
    "rpc_url": "https://sepolia.base.org",
    "chain_id": 84532,
    "explorer": "https://sepolia.basescan.org"
}
```
