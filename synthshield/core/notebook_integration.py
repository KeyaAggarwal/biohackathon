"""
Notebook → Pipeline Integration Demo
=====================================
Shows how to integrate the esm_biosecurity_screening.ipynb research methodology
into the active SynthShield production pipeline.

Steps:
1. Load notebook embeddings (dangerous toxins + benign proteins)
2. Train classifier using notebook methodology
3. Initialize ForensicOrchestrator with trained classifier
4. Screen sequences using ensemble (trained + MLP)
5. Compare results with research performance benchmarks
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, Tuple, Optional

# Import pipeline components
from .trained_classifier import TrainedESMClassifier, NotebookResearchIntegration
from .screening import FunctionalManifoldScreener
from .sentinel_head import SentinelFunctionalHead
from .embeddings import EmbeddingWrapper
from .forensic_orchestrator import ForensicOrchestrator
from ..hardware.blackbox import BlackBoxChain
from ..data.datasets import KNOWN_TOXINS, BENIGN_SEQUENCES


class NotebookPipelineIntegration:
    """
    Bridge between notebook research and production pipeline.
    
    This class:
    1. Loads pre-computed embeddings from notebook (if available)
    2. Trains classifier on notebook's methodology
    3. Integrates with ForensicOrchestrator
    4. Provides performance reporting
    """
    
    def __init__(
        self,
        notebook_embeddings_path: Optional[str] = None,
        embedding_wrapper: Optional[EmbeddingWrapper] = None,
    ):
        """
        Initialize integration.
        
        Args:
            notebook_embeddings_path: Path to notebook's saved embeddings
                                    (data/embeddings/ folder structure)
            embedding_wrapper: Optional EmbeddingWrapper for computing embeddings
        """
        self.notebook_embeddings_path = Path(notebook_embeddings_path) if notebook_embeddings_path else None
        self.embedding_wrapper = embedding_wrapper
        
        # Cached embeddings
        self.dangerous_embeddings: Dict[str, np.ndarray] = {}
        self.benign_embeddings: Dict[str, np.ndarray] = {}
        self.test_embeddings: Dict[str, np.ndarray] = {}
        
        # Trained components
        self.trained_classifier: Optional[TrainedESMClassifier] = None
        self.training_metrics: Dict = {}
        
    def load_notebook_embeddings(self) -> bool:
        """
        Load pre-computed embeddings from notebook.
        
        Expected structure (from esm_biosecurity_screening.ipynb):
        data/embeddings/
          - dangerous.npy
          - benign.npy
          - train.npy
          - test.npy
        
        Returns:
            True if successfully loaded, False otherwise
        """
        if not self.notebook_embeddings_path:
            print("[Integration] No embeddings path provided")
            return False
        
        path = self.notebook_embeddings_path
        
        try:
            # Load numpy arrays
            if (path / "dangerous.npy").exists():
                dangerous_array = np.load(path / "dangerous.npy", allow_pickle=True).item()
                self.dangerous_embeddings = dangerous_array if isinstance(dangerous_array, dict) else {}
                print(f"  ✓ Loaded {len(self.dangerous_embeddings)} dangerous embeddings")
            
            if (path / "benign.npy").exists():
                benign_array = np.load(path / "benign.npy", allow_pickle=True).item()
                self.benign_embeddings = benign_array if isinstance(benign_array, dict) else {}
                print(f"  ✓ Loaded {len(self.benign_embeddings)} benign embeddings")
            
            if (path / "test.npy").exists():
                test_array = np.load(path / "test.npy", allow_pickle=True).item()
                self.test_embeddings = test_array if isinstance(test_array, dict) else {}
                print(f"  ✓ Loaded {len(self.test_embeddings)} test embeddings")
            
            return len(self.dangerous_embeddings) > 0 or len(self.benign_embeddings) > 0
        
        except Exception as e:
            print(f"[Integration] Failed to load embeddings: {e}")
            return False
    
    def compute_embeddings_from_sequences(self) -> bool:
        """
        Compute embeddings from mock sequences if notebook embeddings not available.
        
        This uses the EmbeddingWrapper to generate ESM-2 embeddings from the mock
        toxin/benign datasets in synthshield.data.datasets.
        
        Returns:
            True if successful
        """
        if not self.embedding_wrapper:
            print("[Integration] No embedding wrapper provided")
            return False
        
        print("[Integration] Computing embeddings from mock sequences...")
        
        try:
            # Dangerous sequences
            for name in list(KNOWN_TOXINS.keys())[:10]:  # Limit for demo
                seq = KNOWN_TOXINS[name]
                emb = self.embedding_wrapper.get_embeddings(seq)
                if emb is not None:
                    self.dangerous_embeddings[name] = emb
            
            # Benign sequences
            for name in list(BENIGN_SEQUENCES.keys())[:10]:  # Limit for demo
                seq = BENIGN_SEQUENCES[name]
                emb = self.embedding_wrapper.get_embeddings(seq)
                if emb is not None:
                    self.benign_embeddings[name] = emb
            
            print(f"  ✓ Computed {len(self.dangerous_embeddings)} dangerous embeddings")
            print(f"  ✓ Computed {len(self.benign_embeddings)} benign embeddings")
            
            return len(self.dangerous_embeddings) > 0 and len(self.benign_embeddings) > 0
        
        except Exception as e:
            print(f"[Integration] Failed to compute embeddings: {e}")
            return False
    
    def train_classifier(self) -> bool:
        """
        Train classifier using notebook's methodology.
        
        Returns:
            True if successful
        """
        if len(self.dangerous_embeddings) == 0:
            print("[Integration] No dangerous embeddings available for training")
            return False
        
        if len(self.benign_embeddings) == 0:
            print("[Integration] No benign embeddings available for training")
            return False
        
        print("[Integration] Training classifier using notebook methodology...")
        
        try:
            self.trained_classifier, self.training_metrics = (
                NotebookResearchIntegration.create_classifier_from_notebook_methodology(
                    dangerous_embeddings=self.dangerous_embeddings,
                    benign_embeddings=self.benign_embeddings,
                    test_embeddings=self.test_embeddings if self.test_embeddings else None,
                )
            )
            
            print(f"  ✓ Training complete:")
            print(f"    - Train samples: {self.training_metrics['n_train_total']}")
            print(f"    - Train AUC: {self.training_metrics.get('train_auc', 'N/A'):.3f}")
            if 'test_auc' in self.training_metrics:
                print(f"    - Test AUC: {self.training_metrics['test_auc']:.3f}")
            
            return True
        
        except Exception as e:
            print(f"[Integration] Training failed: {e}")
            return False
    
    def create_orchestrator(
        self,
        hardware_id: str = "SynthShield-Hardware-001",
        tpm_secret: bytes = b"root_of_trust_secret",
        use_mock_l2: bool = True,
        screening_threshold: float = 0.5,
    ) -> Optional[ForensicOrchestrator]:
        """
        Create a ForensicOrchestrator with trained classifier integrated.
        
        Args:
            hardware_id: Hardware identifier
            tpm_secret: Root of trust secret
            use_mock_l2: Use mock L2 (True) or live Ethereum (False)
            screening_threshold: Risk threshold for decisions
        
        Returns:
            ForensicOrchestrator instance or None if failed
        """
        if not self.trained_classifier:
            print("[Integration] No trained classifier available - create one first")
            return None
        
        try:
            # Create MLP head (baseline)
            sentinel_head = SentinelFunctionalHead(
                input_dim=1280,  # ESM-2 embedding dimension
                hidden_dim=512,
                num_blocks=3,
                root_of_trust_key=tpm_secret,
            )
            
            # Create orchestrator with trained classifier
            orchestrator = ForensicOrchestrator(
                hardware_id=hardware_id,
                tpm_secret=tpm_secret,
                use_mock_l2=use_mock_l2,
                sentinel_head=sentinel_head,
                screening_threshold=screening_threshold,
                trained_classifier=self.trained_classifier,
                embedding_wrapper=self.embedding_wrapper,
            )
            
            print(f"[Integration] Created ForensicOrchestrator with trained classifier")
            return orchestrator
        
        except Exception as e:
            print(f"[Integration] Failed to create orchestrator: {e}")
            return False
    
    def get_integration_report(self) -> Dict:
        """Generate integration report."""
        return {
            'dangerous_embeddings_count': len(self.dangerous_embeddings),
            'benign_embeddings_count': len(self.benign_embeddings),
            'test_embeddings_count': len(self.test_embeddings),
            'classifier_trained': self.trained_classifier is not None,
            'training_metrics': self.training_metrics,
            'classifier_stats': (
                self.trained_classifier.get_stats() if self.trained_classifier else None
            ),
        }


def demo_notebook_integration():
    """
    End-to-end demo: integrate notebook research into production pipeline.
    
    This demonstrates:
    1. Training a classifier from mock toxin/benign data
    2. Creating a ForensicOrchestrator with the trained classifier
    3. Screening sequences using the ensemble (trained + MLP)
    4. Comparing results with research benchmarks
    """
    import torch
    
    print("="*70)
    print("NOTEBOOK → PIPELINE INTEGRATION DEMO")
    print("="*70)
    
    # Step 1: Initialize integration
    print("\n[Step 1] Initialize integration...")
    integration = NotebookPipelineIntegration()
    
    # Step 2: Compute embeddings from mock data
    print("\n[Step 2] Compute embeddings from mock sequences...")
    try:
        embedding_wrapper = EmbeddingWrapper()
        integration.embedding_wrapper = embedding_wrapper
        success = integration.compute_embeddings_from_sequences()
        if not success:
            print("  ⚠ Could not compute embeddings")
    except Exception as e:
        print(f"  ⚠ Embedding failed: {e}")
    
    # Step 3: Train classifier
    print("\n[Step 3] Train classifier using notebook methodology...")
    integration.train_classifier()
    
    # Step 4: Create orchestrator
    print("\n[Step 4] Create ForensicOrchestrator with trained classifier...")
    orchestrator = integration.create_orchestrator()
    
    if not orchestrator:
        print("  ✗ Failed to create orchestrator")
        return
    
    # Step 5: Test screening
    print("\n[Step 5] Test screening with ensemble (trained + MLP)...")
    
    # Create dummy embedding
    dummy_embedding = torch.randn(1, 1280)
    
    try:
        result = orchestrator.screener.screen_sequence(
            embeddings=dummy_embedding,
            sentinel_head=orchestrator.sentinel_head,
            sequence="MKTAYIAKQRQISFVK",
        )
        
        print(f"  ✓ Screening result:")
        print(f"    - Risk score: {result['risk_score']:.3f}")
        print(f"    - MLP score: {result['mpl_risk_score']:.3f}")
        print(f"    - Trained score: {result['trained_risk_score']}")
        print(f"    - Decision: {result['decision']}")
        print(f"    - Method: {result['method']}")
    
    except Exception as e:
        print(f"  ✗ Screening failed: {e}")
    
    # Step 6: Report
    print("\n[Step 6] Integration report...")
    report = integration.get_integration_report()
    print(json.dumps(report, indent=2, default=str))
    
    print("\n" + "="*70)
    print("✓ DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    demo_notebook_integration()
