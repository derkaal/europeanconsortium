"""
Memory Manager for European Strategy Consortium

Chroma-based persistent storage and retrieval of strategic cases.
Implements Hybrid B+C approach: immediate feedback + optional long-term outcomes.

Based on ARCHITECTURE_PART2.md Section 5.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings

# Note: Using dict-based cases instead of TypedDict classes
# from src.consortium.state import Case, Outcome, MemoryMetadata, Report


# ==============================================================================
# MEMORY MANAGER
# ==============================================================================

class MemoryManager:
    """
    Manages persistent storage and retrieval of strategic cases using Chroma.
    
    Implements Hybrid B+C approach:
    - Captures immediate user feedback (quality_score 1-5) after recommendation
    - Optionally updates with long-term outcomes when implementation completes
    
    Features:
    - Progressive threshold fallback (3.5 → 3.0 → 2.5)
    - Outcome-based relevance boosting (1.5x for verified positive outcomes)
    - Cold-start handling with confidence penalties
    - Cosine similarity search
    """
    
    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "strategic_cases",
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        Initialize memory manager.
        
        Args:
            persist_directory: Directory for Chroma persistence
            collection_name: Name of Chroma collection
            embedding_model: OpenAI embedding model name
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={
                "description": "Historical cases for European Strategy Consortium",
                "hnsw:space": "cosine"  # Cosine similarity
            }
        )
        
        # Initialize embedding function
        from chromadb.utils import embedding_functions
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=embedding_model
        )
    
    def store_case(self, case: Dict[str, Any]) -> str:
        """
        Store a new strategic case with immediate feedback.
        
        Args:
            case: Complete case with user feedback
        
        Returns:
            Case ID
        
        Raises:
            ValueError: If case is missing required fields
        """
        # Validate required fields
        if not case.get("id"):
            raise ValueError("Case must have an 'id' field")
        if not case.get("query"):
            raise ValueError("Case must have a 'query' field")
        
        # Generate embedding from query + context + recommendation
        embedding_text = self._create_embedding_text(case)
        
        # Get embedding
        try:
            embeddings = self.embedding_function([embedding_text])
            embedding = embeddings[0] if isinstance(embeddings, list) else embeddings
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {e}")
        
        # Prepare metadata for filtering
        # Note: Chroma metadata values must be str, int, float, or bool
        # Complex objects must be JSON-serialized
        metadata = {
            "timestamp": case["timestamp"].isoformat() if isinstance(case["timestamp"], datetime) else str(case["timestamp"]),
            "agents_engaged": json.dumps(case.get("agents_engaged", [])),
            "quality_score": float(case.get("user_feedback", {}).get("quality_score", 0.0)),
            "outcome_status": case.get("outcome", {}).get("status", "not_implemented"),
            "alignment_score": float(case.get("outcome", {}).get("alignment_score") or 0.0),
            "query_length": len(case["query"]),
            "industry": case.get("context", {}).get("industry", "unknown")
        }
        
        # Store in Chroma
        self.collection.add(
            ids=[case["id"]],
            embeddings=[embedding],
            documents=[embedding_text],
            metadatas=[metadata]
        )
        
        return case["id"]
    
    def retrieve_similar_cases(
        self,
        query: str,
        top_k: int = 3,
        min_similarity: float = 0.7,
        min_quality_score: float = 3.5
    ) -> Dict[str, Any]:
        """
        Retrieve similar cases using progressive threshold fallback.
        
        Progressive fallback strategy (from PSEUDOCODE.md Section 4):
        1. Try quality_score >= 3.5
        2. If empty, try quality_score >= 3.0 (confidence penalty -0.20)
        3. If empty, try quality_score >= 2.5 (confidence penalty -0.25)
        
        Args:
            query: Query string to search for
            top_k: Maximum number of cases to return (default: 3)
            min_similarity: Minimum cosine similarity threshold (default: 0.7)
            min_quality_score: Initial quality score threshold (default: 3.5)
        
        Returns:
            Dict with 'cases' (List[Dict]) and 'retrieval_metadata' (MemoryMetadata)
        """
        # Generate query embedding
        try:
            query_embeddings = self.embedding_function([query])
            query_embedding = query_embeddings[0] if isinstance(query_embeddings, list) else query_embeddings
        except Exception as e:
            # Return empty result on embedding failure
            return {
                "cases": [],
                "retrieval_metadata": {
                    "total_matches": 0,
                    "quality_filtered": 0,
                    "returned": 0,
                    "cold_start": True,
                    "confidence_adjustment": -0.15,
                    "warning": f"Embedding generation failed: {e}"
                }
            }
        
        # Progressive threshold fallback
        quality_threshold = min_quality_score
        confidence_penalty = 0.0
        results = None
        
        # Try quality_score >= 3.5
        results = self._query_with_threshold(query_embedding, top_k * 3, quality_threshold)
        
        # Fallback to 3.0
        if len(results["ids"][0]) == 0:
            quality_threshold = 3.0
            confidence_penalty = -0.20
            results = self._query_with_threshold(query_embedding, top_k * 3, quality_threshold)
        
        # Fallback to 2.5
        if len(results["ids"][0]) == 0:
            quality_threshold = 2.5
            confidence_penalty = -0.25
            results = self._query_with_threshold(query_embedding, top_k * 3, quality_threshold)
        
        # Convert results to case dicts with outcome-based weighting
        filtered_cases = []
        
        for i, case_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]
            similarity_score = 1.0 - distance
            
            # Filter by minimum similarity
            if similarity_score < min_similarity:
                continue
            
            # Apply outcome-based weighting (Hybrid C component)
            enhanced_score = similarity_score
            boost_reason = "immediate_feedback_only"
            
            if metadata["outcome_status"] == "implemented":
                if metadata["alignment_score"] >= 4.0:
                    enhanced_score *= 1.5  # 50% boost
                    boost_reason = "verified_positive_outcome"
                elif metadata["alignment_score"] < 3.0:
                    enhanced_score *= 0.7  # 30% penalty
                    boost_reason = "verified_negative_outcome"
            
            case_dict = {
                "id": case_id,
                "query": results["documents"][0][i],
                "similarity_score": similarity_score,
                "enhanced_score": enhanced_score,
                "boost_reason": boost_reason,
                "metadata": metadata
            }
            
            filtered_cases.append(case_dict)
        
        # Sort by enhanced score and take top k
        filtered_cases.sort(key=lambda c: c["enhanced_score"], reverse=True)
        top_cases = filtered_cases[:top_k]
        
        # Create retrieval metadata
        retrieval_metadata = {
            "total_matches": len(results["ids"][0]),
            "quality_filtered": len(filtered_cases),
            "returned": len(top_cases),
            "cold_start": len(top_cases) == 0,
            "confidence_adjustment": confidence_penalty if len(top_cases) == 0 else 0.0,
            "warning": "No historical precedent found" if len(top_cases) == 0 else None
        }
        
        return {
            "cases": top_cases,
            "retrieval_metadata": retrieval_metadata
        }
    
    def update_outcome(self, case_id: str, outcome: Dict[str, Any]) -> bool:
        """
        Update existing case with long-term implementation outcome.
        
        Strategy: Delete and re-insert with updated metadata
        (Chroma doesn't support in-place metadata updates)
        
        Args:
            case_id: ID of case to update
            outcome: Outcome data with status and alignment_score
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing case
            existing = self.collection.get(
                ids=[case_id],
                include=["documents", "embeddings", "metadatas"]
            )
            
            if not existing["ids"]:
                return False
            
            # Update metadata
            metadata = existing["metadatas"][0]
            metadata["outcome_status"] = outcome.get("status", "not_implemented")
            metadata["alignment_score"] = float(outcome.get("alignment_score", 0.0))
            
            # Delete old entry
            self.collection.delete(ids=[case_id])
            
            # Re-insert with updated metadata
            self.collection.add(
                ids=[case_id],
                embeddings=[existing["embeddings"][0]],
                documents=[existing["documents"][0]],
                metadatas=[metadata]
            )
            
            return True
        
        except Exception as e:
            print(f"Error updating case {case_id}: {e}")
            return False
    
    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific case by ID.
        
        Args:
            case_id: Case ID
        
        Returns:
            Case dict or None if not found
        """
        try:
            result = self.collection.get(
                ids=[case_id],
                include=["documents", "metadatas"]
            )
            
            if not result["ids"]:
                return None
            
            return {
                "id": result["ids"][0],
                "query": result["documents"][0],
                "metadata": result["metadatas"][0]
            }
        
        except Exception:
            return None
    
    def count_cases(self) -> int:
        """
        Get total number of cases in collection.
        
        Returns:
            Number of cases
        """
        return self.collection.count()
    
    def delete_case(self, case_id: str) -> bool:
        """
        Delete a case from the collection.
        
        Args:
            case_id: Case ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[case_id])
            return True
        except Exception:
            return False
    
    def clear_all_cases(self) -> bool:
        """
        Clear all cases from the collection.
        
        WARNING: This deletes all data!
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete collection and recreate
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Historical cases for European Strategy Consortium",
                    "hnsw:space": "cosine"
                }
            )
            return True
        except Exception:
            return False
    
    def _query_with_threshold(
        self,
        query_embedding: List[float],
        n_results: int,
        quality_threshold: float
    ) -> Dict[str, Any]:
        """
        Query collection with quality score threshold.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            quality_threshold: Minimum quality score
        
        Returns:
            Chroma query results
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"quality_score": {"$gte": quality_threshold}},
            include=["documents", "metadatas", "distances"]
        )
    
    def _create_embedding_text(self, case: Dict[str, Any]) -> str:
        """
        Create text for embedding generation.
        Combines query, context, and recommendation.
        
        Args:
            case: Case to create embedding text for
        
        Returns:
            Embedding text string
        """
        parts = [
            f"Query: {case['query']}",
            f"Industry: {case.get('context', {}).get('industry', 'N/A')}",
            f"Company Size: {case.get('context', {}).get('company_size', 'N/A')}",
        ]
        
        # Add recommendation if available
        if case.get("final_recommendation"):
            rec = case["final_recommendation"]
            if isinstance(rec, dict):
                parts.append(f"Recommendation: {rec.get('recommendation', 'N/A')}")
            else:
                parts.append(f"Recommendation: {rec}")
        
        # Add agents
        if case.get("agents_engaged"):
            parts.append(f"Agents: {', '.join(case['agents_engaged'])}")
        
        return "\n".join(parts)
    
    def _calculate_confidence_penalty(self, quality_score: float) -> float:
        """
        Calculate confidence penalty based on case quality.
        
        Args:
            quality_score: Quality score (1-5 scale)
        
        Returns:
            Confidence penalty (negative value)
        """
        if quality_score >= 3.5:
            return 0.0
        elif quality_score >= 3.0:
            return -0.20
        elif quality_score >= 2.5:
            return -0.25
        else:
            return -0.30


# ==============================================================================
# GLOBAL INSTANCE
# ==============================================================================

_memory_manager: Optional[MemoryManager] = None


def get_memory_manager(
    persist_directory: str = "./data/chroma",
    collection_name: str = "strategic_cases",
    embedding_model: str = "text-embedding-3-small"
) -> MemoryManager:
    """
    Get global MemoryManager instance (singleton pattern).
    
    Args:
        persist_directory: Directory for Chroma persistence
        collection_name: Name of Chroma collection
        embedding_model: OpenAI embedding model name
    
    Returns:
        MemoryManager instance
    """
    global _memory_manager
    
    if _memory_manager is None:
        _memory_manager = MemoryManager(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedding_model=embedding_model
        )
    
    return _memory_manager
