# SynthShield

## Project Overview
SynthShield is a dual-layered security architecture for benchtop DNA synthesizers. It addresses the "Benchtop Loophole" by integrating real-time functional AI screening with a tamper-evident hardware "Black Box."

### Key Components
1. **Sentinel Neural Head**: AI-based functional screening using ESM-2 embeddings and a custom Residual MLP head.
2. **Forensic Black Box**: Cryptographically chained logging with Merkle Root aggregation.
3. **Biological Root of Trust**: Hardware interlock for solenoid valve control.

## Repository Structure
```
synthshield/
├── core/                # AI Sentinel & Screening Logic
│   ├── sentinel_head.py # PyTorch Residual Head Implementation
│   ├── embeddings.py    # ESM-2/3 Inference Wrapper
│   └── screening.py     # Functional Manifold Projection logic
├── hardware/            # Black Box & Interlock Simulation
│   ├── blackbox.py      # HMAC-chained Logging & Merkle Tree
│   ├── interlock.py     # Solenoid Valve Control Simulation
│   └── edison_window.py # Sliding window assembly detection
├── web/                 # Dashboard Frontend
│   └── src/App.jsx      # React-based BRoT Interface
├── audit/               # Forensic Audit Tools
│   └── verify_chain.py  # Script to validate device integrity
└── data/                # Mock datasets for toxins/evasions
```

## Usage
1. **Setup**:
   - Create a virtual environment: `python3 -m venv uv`
   - Activate the environment: `source uv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

2. **Run Components**:
   - Sentinel Neural Head: `python synthshield/core/sentinel_head.py`
   - Forensic Black Box: `python synthshield/hardware/blackbox.py`
   - Dashboard: `cd synthshield/web && npm start`

3. **Testing**:
   - Run audit tools: `python synthshield/audit/verify_chain.py`

## Development Plan
Refer to `misc/implement_plan.txt` for detailed milestones and coding tasks.