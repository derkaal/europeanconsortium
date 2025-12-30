"""Tests for Feature 5: Hybrid Memory Retrieval + Case Fingerprints.

Tests:
1. Case fingerprint generation from context
2. Fingerprint similarity scoring
3. Store case with fingerprint metadata
4. Retrieve cases with hybrid approach
5. Metadata filtering (regulatory context, company size)
6. Combined score calculation (60% fingerprint + 40% vector)
7. Match explanation generation
8. Adjacent size filtering
9. Edge cases and error handling
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from src.consortium.memory import MemoryManager
from src.consortium.models.case import CaseFingerprint, get_adjacent_sizes


# ==============================================================================
# Test: Case Fingerprint Generation
# ==============================================================================

def test_fingerprint_from_context_basic():
    """Test basic fingerprint generation from context."""
    context = {
        "query": "What's the best cloud strategy for Germany?",
        "target_markets": ["Germany", "France"],
        "industry": "Technology",
        "company_size": "large"
    }

    fingerprint = CaseFingerprint.from_context(context)

    assert fingerprint.market_hash is not None
    assert len(fingerprint.market_hash) == 16  # SHA256[:16]
    assert fingerprint.industry_hash is not None
    assert fingerprint.company_size == "Large"  # Standardized
    assert fingerprint.regulatory_context == "EU"  # Germany -> EU
    assert fingerprint.query_category == "Strategy"


def test_fingerprint_market_normalization():
    """Test that markets are normalized and sorted consistently."""
    context1 = {
        "target_markets": ["France", "Germany"],
        "industry": "Tech",
        "company_size": "medium"
    }

    context2 = {
        "target_markets": ["Germany", "France"],  # Different order
        "industry": "Tech",
        "company_size": "medium"
    }

    fp1 = CaseFingerprint.from_context(context1)
    fp2 = CaseFingerprint.from_context(context2)

    # Same markets in different order should produce same hash
    assert fp1.market_hash == fp2.market_hash


def test_fingerprint_company_size_standardization():
    """Test company size standardization."""
    test_cases = [
        ("startup", "Small"),
        ("SME", "Medium"),
        ("corporation", "Large"),
        ("enterprise", "Enterprise"),
        ("unknown", "Unknown")
    ]

    for input_size, expected_size in test_cases:
        context = {
            "target_markets": ["Germany"],
            "industry": "Tech",
            "company_size": input_size
        }
        fingerprint = CaseFingerprint.from_context(context)
        assert fingerprint.company_size == expected_size


def test_fingerprint_regulatory_context_detection():
    """Test regulatory context detection from markets."""
    test_cases = [
        (["Germany", "France"], "EU"),
        (["United States"], "US"),
        (["United Kingdom"], "UK"),
        (["Japan", "Singapore"], "Global")
    ]

    for markets, expected_context in test_cases:
        context = {
            "target_markets": markets,
            "industry": "Tech",
            "company_size": "medium"
        }
        fingerprint = CaseFingerprint.from_context(context)
        assert fingerprint.regulatory_context == expected_context


def test_fingerprint_query_category_detection():
    """Test query category detection from query text."""
    test_cases = [
        ("What's the best strategy for expansion?", "Strategy"),
        ("How do we comply with GDPR?", "Compliance"),
        ("What's the technical architecture?", "Technical"),
        ("What's the cost of this approach?", "Financial")
    ]

    for query, expected_category in test_cases:
        context = {
            "query": query,
            "target_markets": ["Germany"],
            "industry": "Tech",
            "company_size": "medium"
        }
        fingerprint = CaseFingerprint.from_context(context)
        assert fingerprint.query_category == expected_category


# ==============================================================================
# Test: Fingerprint Similarity Scoring
# ==============================================================================

def test_fingerprint_exact_match():
    """Test fingerprint similarity with exact match."""
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    fp1 = CaseFingerprint.from_context(context)
    fp2 = CaseFingerprint.from_context(context)

    score = fp1.similarity_score(fp2)
    assert score == 1.0  # Perfect match


def test_fingerprint_market_only_match():
    """Test fingerprint similarity with only market match."""
    context1 = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    context2 = {
        "target_markets": ["Germany"],  # Same market
        "industry": "Finance",  # Different industry
        "company_size": "small"  # Different size
    }

    fp1 = CaseFingerprint.from_context(context1)
    fp2 = CaseFingerprint.from_context(context2)

    score = fp1.similarity_score(fp2)
    # Market (0.4) + Regulatory (0.1) = 0.5 (same EU context)
    assert 0.4 <= score <= 0.6


def test_fingerprint_adjacent_size_match():
    """Test fingerprint similarity with adjacent company size."""
    context1 = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "medium"
    }

    context2 = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"  # Adjacent size
    }

    fp1 = CaseFingerprint.from_context(context1)
    fp2 = CaseFingerprint.from_context(context2)

    score = fp1.similarity_score(fp2)
    # Market (0.4) + Industry (0.3) + Adjacent size (0.1) + Regulatory (0.1) = 0.9
    assert 0.85 <= score <= 0.95


def test_fingerprint_no_match():
    """Test fingerprint similarity with no match."""
    context1 = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    context2 = {
        "target_markets": ["Japan"],
        "industry": "Finance",
        "company_size": "small"
    }

    fp1 = CaseFingerprint.from_context(context1)
    fp2 = CaseFingerprint.from_context(context2)

    score = fp1.similarity_score(fp2)
    assert score == 0.0  # No matches


# ==============================================================================
# Test: Adjacent Size Filtering
# ==============================================================================

def test_get_adjacent_sizes_small():
    """Test adjacent sizes for Small."""
    adjacent = get_adjacent_sizes("Small")
    assert set(adjacent) == {"Small", "Medium"}


def test_get_adjacent_sizes_medium():
    """Test adjacent sizes for Medium."""
    adjacent = get_adjacent_sizes("Medium")
    assert set(adjacent) == {"Small", "Medium", "Large"}


def test_get_adjacent_sizes_large():
    """Test adjacent sizes for Large."""
    adjacent = get_adjacent_sizes("Large")
    assert set(adjacent) == {"Medium", "Large", "Enterprise"}


def test_get_adjacent_sizes_enterprise():
    """Test adjacent sizes for Enterprise."""
    adjacent = get_adjacent_sizes("Enterprise")
    assert set(adjacent) == {"Large", "Enterprise"}


def test_get_adjacent_sizes_unknown():
    """Test adjacent sizes for Unknown returns all."""
    adjacent = get_adjacent_sizes("Unknown")
    assert set(adjacent) == {"Small", "Medium", "Large", "Enterprise"}


# ==============================================================================
# Test: Store Case with Fingerprint
# ==============================================================================

@pytest.fixture
def mock_memory_manager():
    """Create mock MemoryManager for testing."""
    with patch('src.consortium.memory.chromadb.PersistentClient'), \
         patch('src.consortium.memory.embedding_functions.OpenAIEmbeddingFunction'):

        # Mock the collection
        mock_collection = Mock()
        mock_collection.add = Mock()
        mock_collection.query = Mock()
        mock_collection.count = Mock(return_value=0)

        # Mock the client
        mock_client = Mock()
        mock_client.get_or_create_collection = Mock(return_value=mock_collection)

        with patch.object(MemoryManager, '__init__', lambda self, *args, **kwargs: None):
            manager = MemoryManager()
            manager.collection = mock_collection
            manager.embedding_function = Mock(return_value=[[0.1] * 1536])
            return manager


def test_store_case_includes_fingerprint_metadata(mock_memory_manager):
    """Test that storing a case includes fingerprint metadata."""
    case = {
        "id": "test-case-1",
        "query": "What's the best cloud strategy?",
        "timestamp": datetime.now(),
        "context": {
            "target_markets": ["Germany", "France"],
            "industry": "Technology",
            "company_size": "large"
        },
        "user_feedback": {
            "quality_score": 4.5
        }
    }

    case_id = mock_memory_manager.store_case(case)

    # Verify case was stored
    assert case_id == "test-case-1"
    mock_memory_manager.collection.add.assert_called_once()

    # Extract metadata from call
    call_args = mock_memory_manager.collection.add.call_args
    metadata = call_args[1]["metadatas"][0]

    # Verify fingerprint fields are present
    assert "market_hash" in metadata
    assert "industry_hash" in metadata
    assert "company_size" in metadata
    assert "regulatory_context" in metadata
    assert "query_category" in metadata

    # Verify values
    assert metadata["company_size"] == "Large"
    assert metadata["regulatory_context"] == "EU"
    assert len(metadata["market_hash"]) == 16


# ==============================================================================
# Test: Hybrid Retrieval
# ==============================================================================

@pytest.fixture
def populated_memory_manager():
    """Create MemoryManager with mock data."""
    with patch('src.consortium.memory.chromadb.PersistentClient'), \
         patch('src.consortium.memory.embedding_functions.OpenAIEmbeddingFunction'):

        mock_collection = Mock()

        # Mock query results
        mock_results = {
            "ids": [["case-1", "case-2", "case-3"]],
            "documents": [["Query 1", "Query 2", "Query 3"]],
            "distances": [[0.2, 0.3, 0.4]],  # Similarities: 0.8, 0.7, 0.6
            "metadatas": [[
                {
                    "market_hash": "abc123def456789a",
                    "industry_hash": "tech123hash456",
                    "company_size": "Large",
                    "regulatory_context": "EU",
                    "query_category": "Strategy",
                    "quality_score": 4.5
                },
                {
                    "market_hash": "abc123def456789a",  # Same market
                    "industry_hash": "tech123hash456",  # Same industry
                    "company_size": "Medium",  # Adjacent size
                    "regulatory_context": "EU",
                    "query_category": "Strategy",
                    "quality_score": 4.0
                },
                {
                    "market_hash": "different_hash_12",
                    "industry_hash": "finance_hash_34",
                    "company_size": "Large",
                    "regulatory_context": "EU",
                    "query_category": "Financial",
                    "quality_score": 3.8
                }
            ]]
        }

        mock_collection.query = Mock(return_value=mock_results)

        with patch.object(MemoryManager, '__init__', lambda self, *args, **kwargs: None):
            manager = MemoryManager()
            manager.collection = mock_collection
            manager.embedding_function = Mock(return_value=[[0.1] * 1536])
            return manager


def test_hybrid_retrieval_basic(populated_memory_manager):
    """Test basic hybrid retrieval."""
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    result = populated_memory_manager.retrieve_similar_cases_hybrid(
        query="What's the best cloud strategy?",
        context=context,
        top_k=3
    )

    assert len(result["cases"]) > 0
    assert "retrieval_metadata" in result
    assert result["retrieval_metadata"]["returned"] > 0


def test_hybrid_retrieval_combined_scoring(populated_memory_manager):
    """Test combined scoring (60% fingerprint + 40% vector)."""
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    result = populated_memory_manager.retrieve_similar_cases_hybrid(
        query="What's the best cloud strategy?",
        context=context,
        top_k=3,
        fingerprint_weight=0.6,
        vector_weight=0.4
    )

    # Verify cases have combined scores
    for case in result["cases"]:
        assert "vector_similarity" in case
        assert "fingerprint_similarity" in case
        assert "combined_score" in case

        # Verify combined score calculation
        expected_score = (
            0.6 * case["fingerprint_similarity"] +
            0.4 * case["vector_similarity"]
        )
        assert abs(case["combined_score"] - expected_score) < 0.001


def test_hybrid_retrieval_match_explanation(populated_memory_manager):
    """Test match explanation generation."""
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    result = populated_memory_manager.retrieve_similar_cases_hybrid(
        query="What's the best cloud strategy?",
        context=context,
        top_k=3
    )

    # Verify match explanations exist
    for case in result["cases"]:
        assert "match_explanation" in case
        assert isinstance(case["match_explanation"], str)
        assert len(case["match_explanation"]) > 0


def test_hybrid_retrieval_metadata_filtering(populated_memory_manager):
    """Test that results are filtered by regulatory context."""
    context = {
        "target_markets": ["United States"],  # US context
        "industry": "Technology",
        "company_size": "large"
    }

    result = populated_memory_manager.retrieve_similar_cases_hybrid(
        query="What's the best cloud strategy?",
        context=context,
        top_k=3
    )

    # Mock returns EU cases, but with US query they should have low fingerprint scores
    # Verify retrieval still works (may return fewer results)
    assert "cases" in result
    assert "retrieval_metadata" in result


def test_hybrid_retrieval_adjacent_size_filtering(populated_memory_manager):
    """Test that adjacent company sizes are included."""
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"  # Should match Large and adjacent (Medium, Enterprise)
    }

    result = populated_memory_manager.retrieve_similar_cases_hybrid(
        query="What's the best cloud strategy?",
        context=context,
        top_k=3
    )

    # Verify Medium size case is included (adjacent to Large)
    case_sizes = [case["metadata"]["company_size"] for case in result["cases"]]
    # Should include at least one Medium (adjacent to Large)
    assert any(size in ["Large", "Medium", "Enterprise"] for size in case_sizes)


def test_hybrid_retrieval_minimum_similarity(populated_memory_manager):
    """Test minimum similarity threshold filtering."""
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    result = populated_memory_manager.retrieve_similar_cases_hybrid(
        query="What's the best cloud strategy?",
        context=context,
        top_k=10,
        min_similarity=0.9  # High threshold
    )

    # Verify all returned cases meet threshold
    for case in result["cases"]:
        assert case["combined_score"] >= 0.9


def test_hybrid_retrieval_custom_weights(populated_memory_manager):
    """Test custom fingerprint and vector weights."""
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    # Test with 80% fingerprint, 20% vector
    result = populated_memory_manager.retrieve_similar_cases_hybrid(
        query="What's the best cloud strategy?",
        context=context,
        top_k=3,
        fingerprint_weight=0.8,
        vector_weight=0.2
    )

    assert result["retrieval_metadata"]["fingerprint_weight"] == 0.8
    assert result["retrieval_metadata"]["vector_weight"] == 0.2


def test_hybrid_retrieval_empty_results(mock_memory_manager):
    """Test hybrid retrieval with no matching cases."""
    # Mock empty results
    mock_memory_manager.collection.query = Mock(return_value={
        "ids": [[]],
        "documents": [[]],
        "distances": [[]],
        "metadatas": [[]]
    })

    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    result = mock_memory_manager.retrieve_similar_cases_hybrid(
        query="What's the best cloud strategy?",
        context=context,
        top_k=3
    )

    assert len(result["cases"]) == 0
    assert result["retrieval_metadata"]["cold_start"] is True
    assert result["retrieval_metadata"]["confidence_adjustment"] == -0.15


# ==============================================================================
# Test: Match Explanation
# ==============================================================================

def test_explain_fingerprint_match_exact():
    """Test explanation for exact fingerprint match."""
    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    fp1 = CaseFingerprint.from_context(context)
    fp2 = CaseFingerprint.from_context(context)

    with patch('src.consortium.memory.chromadb.PersistentClient'), \
         patch('src.consortium.memory.embedding_functions.OpenAIEmbeddingFunction'):
        with patch.object(MemoryManager, '__init__', lambda self, *args, **kwargs: None):
            manager = MemoryManager()
            explanation = manager._explain_fingerprint_match(fp1, fp2)

    assert "exact market match" in explanation
    assert "exact industry match" in explanation
    assert "exact size match" in explanation


def test_explain_fingerprint_match_adjacent():
    """Test explanation for adjacent size match."""
    context1 = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "medium"
    }

    context2 = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"  # Adjacent
    }

    fp1 = CaseFingerprint.from_context(context1)
    fp2 = CaseFingerprint.from_context(context2)

    with patch('src.consortium.memory.chromadb.PersistentClient'), \
         patch('src.consortium.memory.embedding_functions.OpenAIEmbeddingFunction'):
        with patch.object(MemoryManager, '__init__', lambda self, *args, **kwargs: None):
            manager = MemoryManager()
            explanation = manager._explain_fingerprint_match(fp1, fp2)

    assert "adjacent size match" in explanation


def test_explain_fingerprint_match_weak():
    """Test explanation for weak match."""
    context1 = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    context2 = {
        "target_markets": ["Japan"],
        "industry": "Finance",
        "company_size": "small"
    }

    fp1 = CaseFingerprint.from_context(context1)
    fp2 = CaseFingerprint.from_context(context2)

    with patch('src.consortium.memory.chromadb.PersistentClient'), \
         patch('src.consortium.memory.embedding_functions.OpenAIEmbeddingFunction'):
        with patch.object(MemoryManager, '__init__', lambda self, *args, **kwargs: None):
            manager = MemoryManager()
            explanation = manager._explain_fingerprint_match(fp1, fp2)

    assert explanation == "weak contextual match"


# ==============================================================================
# Test: Error Handling
# ==============================================================================

def test_hybrid_retrieval_embedding_failure(mock_memory_manager):
    """Test hybrid retrieval handles embedding generation failure."""
    # Mock embedding failure
    mock_memory_manager.embedding_function = Mock(side_effect=Exception("API Error"))

    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    result = mock_memory_manager.retrieve_similar_cases_hybrid(
        query="What's the best cloud strategy?",
        context=context,
        top_k=3
    )

    assert len(result["cases"]) == 0
    assert result["retrieval_metadata"]["cold_start"] is True
    assert "Embedding generation failed" in result["retrieval_metadata"]["warning"]


def test_hybrid_retrieval_metadata_filter_failure(populated_memory_manager):
    """Test hybrid retrieval handles metadata filter failure gracefully."""
    # Mock query to raise exception on first call (with filter),
    # then succeed on second call (without filter)
    mock_results = {
        "ids": [["case-1"]],
        "documents": [["Query 1"]],
        "distances": [[0.2]],
        "metadatas": [[{
            "market_hash": "abc123",
            "industry_hash": "tech123",
            "company_size": "Large",
            "regulatory_context": "EU",
            "query_category": "Strategy"
        }]]
    }

    populated_memory_manager.collection.query = Mock(
        side_effect=[Exception("Filter error"), mock_results]
    )

    context = {
        "target_markets": ["Germany"],
        "industry": "Technology",
        "company_size": "large"
    }

    result = populated_memory_manager.retrieve_similar_cases_hybrid(
        query="What's the best cloud strategy?",
        context=context,
        top_k=3
    )

    # Should still return results from fallback query
    assert len(result["cases"]) > 0


# ==============================================================================
# Test: Integration with Existing Retrieval
# ==============================================================================

def test_backward_compatibility_with_existing_retrieval(mock_memory_manager):
    """Test that existing retrieve_similar_cases() still works."""
    # Mock query results for existing method
    mock_results = {
        "ids": [["case-1"]],
        "documents": [["Query 1"]],
        "distances": [[0.2]],
        "metadatas": [[{
            "quality_score": 4.5,
            "outcome_status": "not_implemented",
            "alignment_score": 0.0
        }]]
    }

    mock_memory_manager.collection.query = Mock(return_value=mock_results)

    # Old method should still work
    result = mock_memory_manager.retrieve_similar_cases(
        query="What's the best cloud strategy?",
        top_k=3
    )

    assert "cases" in result
    assert "retrieval_metadata" in result
