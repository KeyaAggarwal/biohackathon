"""
Trained ESM Classifier Module
========================================
Integrates the notebook's research methodology into the active pipeline.

This module:
1. Manages a trained LogisticRegression classifier on ESM embeddings
2. Maintains reference embeddings of known dangerous proteins
3. Provides cosine similarity-based threat detection (complementary to MLP)
4. Supports both cosine-similarity scoring and learned classifier scoring

Research Foundation:
- Notebook: esm_biosecurity_screening.ipynb
- Method: Train on toxin families, test on remote homologs (30% identity cluster split)
- Performance: 84% catch rate on evasion sequences, AUC 0.977 vs BLAST AUC 0.711
- Key insight: ESM embeddings capture functional similarity where sequence-based methods fail
"""

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import json
import pickle
from typing import Dict, List, Tuple, Optional
import hashlib


class TrainedESMClassifier:
    """
    Production classifier integrating notebook research into active pipeline.
    
    Combines two scoring methods:
    1. Cosine similarity to reference dangerous proteins (interpretable, fast)
    2. Learned LogisticRegression classifier (trained on balanced dataset)
    
    Both scores are provided; system can use either or ensemble them.
    """
    
    def __init__(
        self,
        reference_embeddings: Optional[Dict[str, np.ndarray]] = None,
        classifier: Optional[LogisticRegression] = None,
        scaler: Optional[StandardScaler] = None,
        similarity_threshold: float = 0.972,
        classifier_threshold: float = 0.5,
        enable_cosine_mode: bool = True,
        enable_classifier_mode: bool = True
    ):
        """
        Initialize trained classifier.
        
        Args:
            reference_embeddings: Dict of {name: embedding} for dangerous proteins
            classifier: Trained LogisticRegression model (from notebook training)
            scaler: StandardScaler fitted to training embeddings
            similarity_threshold: Cosine similarity threshold for flagging (0.972 from notebook)
            classifier_threshold: Probability threshold for classifier (0.5 from notebook)
            enable_cosine_mode: Use cosine similarity scoring
            enable_classifier_mode: Use learned classifier scoring
        """
        self.reference_embeddings = reference_embeddings or {}
        self.classifier = classifier
        self.scaler = scaler
        self.similarity_threshold = similarity_threshold
        self.classifier_threshold = classifier_threshold
        self.enable_cosine_mode = enable_cosine_mode
        self.enable_classifier_mode = enable_classifier_mode
        
        # Mode tracking
        self.mode = "ensemble"  # ensemble, cosine_only, classifier_only
        
    def score_embedding_cosine(
        self,
        embedding: np.ndarray,
        return_closest: bool = False
    ) -> Tuple[float, Optional[str]]:
        """
        Score embedding by max cosine similarity to reference dangerous proteins.
        
        This is the interpretable method from the notebook: compute similarity to
        all known dangerous sequences and flag if max similarity exceeds threshold.
        
        Args:
            embedding: 1D numpy array (1280D for ESM-2)
            return_closest: If True, return (score, closest_protein_name)
        
        Returns:
            (max_similarity_score, closest_protein_name or None)
        """
        if not self.reference_embeddings:
            return 0.0, None
        
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        elif embedding.shape[0] == 1:
            pass
        else:
            # Multiple embeddings: take first one
            embedding = embedding[:1]
        
        max_sim = -1.0
        closest_name = None
        
        for ref_name, ref_emb in self.reference_embeddings.items():
            if ref_emb.ndim == 1:
                ref_emb = ref_emb.reshape(1, -1)
            sim = cosine_similarity(embedding, ref_emb)[0, 0]
            if sim > max_sim:
                max_sim = sim
                closest_name = ref_name
        
        return float(max_sim), closest_name
    
    def score_embedding_classifier(self, embedding: np.ndarray) -> float:
        """
        Score embedding using trained LogisticRegression classifier.
        
        This is the learned method from notebook training.
        
        Args:
            embedding: 1D or 2D numpy array
        
        Returns:
            Probability (0.0-1.0) of being dangerous
        """
        if self.classifier is None or self.scaler is None:
            return 0.5  # Neutral if no classifier available
        
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        try:
            embedding_scaled = self.scaler.transform(embedding)
            proba = self.classifier.predict_proba(embedding_scaled)[0, 1]
            return float(proba)
        except Exception as e:
            print(f"[TrainedClassifier] Classifier scoring failed: {e}")
            return 0.5
    
    def score_embedding(
        self,
        embedding: np.ndarray,
        mode: Optional[str] = None,
        return_details: bool = False
    ) -> Dict:
        """
        Score embedding using configured mode(s).
        
        Args:
            embedding: ESM embedding (1D or 2D numpy array)
            mode: Override default mode (ensemble, cosine_only, classifier_only)
            return_details: If True, return full detail dict; else return {'risk_score': float}
        
        Returns:
            Dict with keys:
            - 'risk_score': Main risk score (0.0-1.0)
            - 'cosine_score': Max cosine similarity to references (if cosine mode enabled)
            - 'cosine_closest': Closest reference protein name
            - 'classifier_score': Classifier probability (if classifier mode enabled)
            - 'flagged_cosine': Bool if cosine_score > threshold
            - 'flagged_classifier': Bool if classifier_score > threshold
            - 'flagged': Bool if any method flags it
            - 'method': Which method produced final risk_score
        """
        mode = mode or self.mode
        
        cosine_score = None
        cosine_closest = None
        classifier_score = None
        flagged_cosine = False
        flagged_classifier = False
        
        # Compute cosine score if enabled
        if self.enable_cosine_mode:
            cosine_score, cosine_closest = self.score_embedding_cosine(embedding)
            flagged_cosine = cosine_score > self.similarity_threshold
        
        # Compute classifier score if enabled
        if self.enable_classifier_mode:
            classifier_score = self.score_embedding_classifier(embedding)
            flagged_classifier = classifier_score > self.classifier_threshold
        
        # Determine final risk score based on mode
        if mode == "cosine_only":
            final_score = cosine_score if cosine_score is not None else 0.5
            final_method = "cosine_similarity"
            flagged = flagged_cosine
        elif mode == "classifier_only":
            final_score = classifier_score if classifier_score is not None else 0.5
            final_method = "trained_classifier"
            flagged = flagged_classifier
        else:  # ensemble
            # Ensemble: flag if either method flags
            scores = []
            if cosine_score is not None:
                scores.append(cosine_score)
            if classifier_score is not None:
                scores.append(classifier_score)
            
            if scores:
                final_score = np.mean(scores)
            else:
                final_score = 0.5
            
            final_method = "ensemble"
            flagged = flagged_cosine or flagged_classifier
        
        result = {
            'risk_score': final_score,
            'flagged': flagged,
            'method': final_method,
        }
        
        if return_details:
            result.update({
                'cosine_score': cosine_score,
                'cosine_closest': cosine_closest,
                'flagged_cosine': flagged_cosine,
                'classifier_score': classifier_score,
                'flagged_classifier': flagged_classifier,
            })
        
        return result
    
    def add_reference_embedding(self, name: str, embedding: np.ndarray) -> None:
        """Add a reference dangerous protein embedding."""
        if embedding.ndim != 1:
            embedding = embedding.flatten()
        self.reference_embeddings[name] = embedding
    
    def set_reference_embeddings(self, embeddings_dict: Dict[str, np.ndarray]) -> None:
        """Replace all reference embeddings."""
        self.reference_embeddings = embeddings_dict
    
    def save(self, path: str) -> None:
        """Save classifier to disk."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save classifier and scaler
        if self.classifier and self.scaler:
            with open(path / "classifier.pkl", "wb") as f:
                pickle.dump({
                    'classifier': self.classifier,
                    'scaler': self.scaler,
                    'similarity_threshold': self.similarity_threshold,
                    'classifier_threshold': self.classifier_threshold,
                }, f)
        
        # Save reference embeddings
        ref_embs = {
            k: v.tolist() if isinstance(v, np.ndarray) else v
            for k, v in self.reference_embeddings.items()
        }
        with open(path / "reference_embeddings.json", "w") as f:
            json.dump(ref_embs, f)
        
        print(f"[TrainedClassifier] Saved to {path}")
    
    @classmethod
    def load(cls, path: str) -> 'TrainedESMClassifier':
        """Load classifier from disk."""
        path = Path(path)
        
        classifier = None
        scaler = None
        similarity_threshold = 0.972
        classifier_threshold = 0.5
        
        # Load classifier and scaler
        if (path / "classifier.pkl").exists():
            with open(path / "classifier.pkl", "rb") as f:
                data = pickle.load(f)
                classifier = data['classifier']
                scaler = data['scaler']
                similarity_threshold = data.get('similarity_threshold', 0.972)
                classifier_threshold = data.get('classifier_threshold', 0.5)
        
        # Load reference embeddings
        reference_embeddings = {}
        if (path / "reference_embeddings.json").exists():
            with open(path / "reference_embeddings.json", "r") as f:
                ref_dict = json.load(f)
                reference_embeddings = {
                    k: np.array(v) for k, v in ref_dict.items()
                }
        
        instance = cls(
            reference_embeddings=reference_embeddings,
            classifier=classifier,
            scaler=scaler,
            similarity_threshold=similarity_threshold,
            classifier_threshold=classifier_threshold,
        )
        print(f"[TrainedClassifier] Loaded from {path}")
        return instance
    
    def get_stats(self) -> Dict:
        """Get classifier statistics."""
        return {
            'n_reference_embeddings': len(self.reference_embeddings),
            'has_classifier': self.classifier is not None,
            'has_scaler': self.scaler is not None,
            'similarity_threshold': self.similarity_threshold,
            'classifier_threshold': self.classifier_threshold,
            'enable_cosine_mode': self.enable_cosine_mode,
            'enable_classifier_mode': self.enable_classifier_mode,
            'mode': self.mode,
        }


class NotebookResearchIntegration:
    """
    Utility for integrating notebook research into production pipeline.
    
    This class bridges the notebook's training methodology (esm_biosecurity_screening.ipynb)
    with the active system components.
    """
    
    @staticmethod
    def create_classifier_from_notebook_methodology(
        dangerous_embeddings: Dict[str, np.ndarray],
        benign_embeddings: Dict[str, np.ndarray],
        test_embeddings: Optional[Dict[str, np.ndarray]] = None,
        test_labels: Optional[Dict[str, int]] = None,
    ) -> Tuple[TrainedESMClassifier, Dict]:
        """
        Train a classifier following the notebook's research methodology.
        
        Args:
            dangerous_embeddings: Dict of {name: embedding} for toxins
            benign_embeddings: Dict of {name: embedding} for safe proteins
            test_embeddings: Optional holdout test set for evaluation
            test_labels: Optional labels for test set (1=dangerous, 0=benign)
        
        Returns:
            (TrainedESMClassifier instance, training_metrics_dict)
        """
        from sklearn.metrics import roc_auc_score, classification_report
        
        # Build training set
        X_train = []
        y_train = []
        
        for emb in dangerous_embeddings.values():
            if isinstance(emb, np.ndarray):
                X_train.append(emb)
                y_train.append(1)
        
        for emb in benign_embeddings.values():
            if isinstance(emb, np.ndarray):
                X_train.append(emb)
                y_train.append(0)
        
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        # Train
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        clf = LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            C=1.0,
            random_state=42
        )
        clf.fit(X_train_scaled, y_train)
        
        # Evaluate on training set
        train_pred_proba = clf.predict_proba(X_train_scaled)[:, 1]
        train_auc = roc_auc_score(y_train, train_pred_proba)
        
        metrics = {
            'n_train_dangerous': len(dangerous_embeddings),
            'n_train_benign': len(benign_embeddings),
            'n_train_total': len(X_train),
            'train_auc': train_auc,
        }
        
        # Evaluate on test set if provided
        if test_embeddings and test_labels:
            X_test = np.array(list(test_embeddings.values()))
            y_test = np.array([test_labels[k] for k in test_embeddings.keys()])
            
            X_test_scaled = scaler.transform(X_test)
            test_pred_proba = clf.predict_proba(X_test_scaled)[:, 1]
            test_auc = roc_auc_score(y_test, test_pred_proba)
            
            metrics['test_auc'] = test_auc
            metrics['n_test_total'] = len(X_test)
            metrics['classification_report'] = classification_report(
                y_test,
                test_pred_proba > 0.5,
                output_dict=True
            )
        
        # Create classifier with reference embeddings (dangerous proteins)
        classifier_instance = TrainedESMClassifier(
            reference_embeddings=dangerous_embeddings,
            classifier=clf,
            scaler=scaler,
            similarity_threshold=0.972,  # From notebook results
            classifier_threshold=0.5,
        )
        
        return classifier_instance, metrics


# Example usage
if __name__ == "__main__":
    print("TrainedESMClassifier loaded successfully")
    
    # Demo: create a classifier with mock embeddings
    mock_dangerous = {
        "ricin": np.random.randn(1280),
        "botulinum": np.random.randn(1280),
    }
    mock_benign = {
        "GFP": np.random.randn(1280),
        "lysozyme": np.random.randn(1280),
    }
    
    clf = TrainedESMClassifier(reference_embeddings=mock_dangerous)
    test_emb = np.random.randn(1280)
    result = clf.score_embedding(test_emb, return_details=True)
    print(f"Score result: {result}")
    print(f"Stats: {clf.get_stats()}")
