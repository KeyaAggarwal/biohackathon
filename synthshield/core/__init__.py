# Core module

# Research-to-production integration (notebook)
from .trained_classifier import TrainedESMClassifier, NotebookResearchIntegration
from .notebook_integration import NotebookPipelineIntegration, demo_notebook_integration

# Active components
from .screening import FunctionalManifoldScreener
from .sentinel_head import SentinelFunctionalHead
from .embeddings import EmbeddingWrapper
from .forensic_orchestrator import ForensicOrchestrator

__all__ = [
    # Integration
    'TrainedESMClassifier',
    'NotebookResearchIntegration',
    'NotebookPipelineIntegration',
    'demo_notebook_integration',
    # Core
    'FunctionalManifoldScreener',
    'SentinelFunctionalHead',
    'EmbeddingWrapper',
    'ForensicOrchestrator',
]
