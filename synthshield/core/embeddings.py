"""
Embedding Projection Logic via ESM-2/3 Protein Language Models

This module wraps the Facebook ESM (Evolutionary Scale Modeling) transformer for 
generating high-quality functional embeddings from DNA/protein sequences.

Key features:
- Automatic device detection (GPU/CPU)
- Batch processing support for efficiency
- Mean pooling for sequence-level embeddings
- Compatibility with ESM-2 and ESM-3 models
- Configurable model sizes (8M to 650M parameters)

Model options:
- facebook/esm2_t6_8M_UR50D (small, fast)
- facebook/esm2_t33_650M_UR50D (large, accurate - default)
- facebook/esm2_t36_3B_UR50D (very large, research only)

The embeddings are used as input to the Sentinel Head for functional manifold projection.
"""

import torch
from transformers import AutoModel, AutoTokenizer
from typing import Union, List, Optional


class EmbeddingWrapper:
    """
    Wrapper for ESM-2/3 embeddings used in the Sentinel functional head.
    
    Generates 1280-dimensional embeddings representing the functional properties
    of DNA/protein sequences. These embeddings are then projected onto the
    functional manifold via the Sentinel MLP head.
    """
    
    def __init__(self, model_name: str = "facebook/esm2_t33_650M_UR50D"):
        """
        Initialize embedding model.
        
        Args:
            model_name: Hugging Face model identifier. Default is ESM-2 650M.
                       Options include:
                       - facebook/esm2_t6_8M_UR50D (fast)
                       - facebook/esm2_t33_650M_UR50D (recommended)
                       - facebook/esm2_t36_3B_UR50D (very large)
        
        Raises:
            RuntimeError: If model cannot be loaded from Hugging Face
            RuntimeError: If GPU not available but CUDA requested
        """
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            print(f"[ESM Embedding] Loaded {model_name} on {self.device}")
        except Exception as e:
            raise RuntimeError(f"Failed to load ESM model {model_name}: {e}")

    def get_embeddings(
        self,
        sequences: Union[str, List[str]],
        batch_size: int = 8,
        return_cpu: bool = True
    ) -> torch.Tensor:
        """
        Generate ESM-2 embeddings for one or more sequences.
        
        Processing:
        1. Tokenize sequences with max length 1024
        2. Run through transformer model (no gradient computation)
        3. Apply mean pooling across tokens
        4. Return embeddings on CPU or GPU
        
        Args:
            sequences: Single sequence string or list of sequences
            batch_size: Number of sequences to process simultaneously (default 8).
                       Larger batch size = faster but uses more memory.
            return_cpu: If True, return embeddings on CPU (default). If False, GPU.
        
        Returns:
            Tensor of shape:
            - (1280,) if single sequence
            - (n_sequences, 1280) if batch
        
        Raises:
            TypeError: If sequences is not str or list
            RuntimeError: If tokenization or model inference fails
        
        Example:
            >>> wrapper = EmbeddingWrapper()
            >>> seq = "MVKRK..."  # Protein sequence
            >>> emb = wrapper.get_embeddings(seq)
            >>> print(emb.shape)  # torch.Size([1280])
        """
        if isinstance(sequences, str):
            sequences = [sequences]
        elif not isinstance(sequences, list):
            raise TypeError(f"Expected str or list, got {type(sequences)}")
        
        all_embeddings = []
        
        with torch.no_grad():
            for i in range(0, len(sequences), batch_size):
                batch = sequences[i:i+batch_size]
                
                try:
                    inputs = self.tokenizer(
                        batch,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=1024
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    outputs = self.model(**inputs)
                    # Mean pool over tokens to get sequence-level embeddings
                    embeddings = outputs.last_hidden_state.mean(dim=1)
                    
                    if return_cpu:
                        embeddings = embeddings.cpu()
                    
                    all_embeddings.append(embeddings)
                
                except Exception as e:
                    raise RuntimeError(f"Embedding generation failed for batch: {e}")
        
        result = torch.cat(all_embeddings, dim=0)
        
        # Return shape (1280,) for single sequence, (n, 1280) for batch
        if result.shape[0] == 1 and len(sequences) == 1:
            result = result.squeeze(0)
        
        return result


# Example usage
if __name__ == "__main__":
    wrapper = EmbeddingWrapper()
    sequences = ["MKTAYIAKQRQISFVKSHFSRQDILDLWQ", "GAVLGGAGGLGGLGGLG"]
    embeddings = wrapper.get_embeddings(sequences)
    print("Embeddings shape:", embeddings.shape)
    print("First 10 dimensions:", embeddings[0][:10])