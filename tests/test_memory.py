"""Tests for Memory Manager."""
import pytest
import sys
from datetime import datetime
import tempfile
import shutil

sys.path.insert(0, '.')


class TestMemoryManager:
    """Test MemoryManager functionality."""
    
    def test_memory_manager_singleton(self):
        """Test MemoryManager singleton pattern."""
        from src.consortium.memory import MemoryManager
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        try:
            manager1 = MemoryManager(persist_directory=temp_dir)
            manager2 = MemoryManager(persist_directory=temp_dir)
            
            # Both should reference same collection
            assert manager1.collection.name == manager2.collection.name
            print("✓ MemoryManager singleton works")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_memory_manager_initialization(self):
        """Test MemoryManager can be initialized."""
        from src.consortium.memory import MemoryManager
        
        # Use temp directory to avoid conflicts
        temp_dir = tempfile.mkdtemp()
        try:
            manager = MemoryManager(persist_directory=temp_dir)
            assert manager is not None
            assert manager.collection is not None
            assert manager.collection.name == "strategic_cases"
            print("✓ MemoryManager initialized")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_memory_manager_store_case(self):
        """Test storing a case."""
        from src.consortium.memory import MemoryManager
        
        temp_dir = tempfile.mkdtemp()
        try:
            manager = MemoryManager(persist_directory=temp_dir)
            
            # Create case with required fields including timestamp
            case = {
                "id": f"test-{datetime.now().isoformat()}",
                "query": "Test query for memory storage",
                "context": {"industry": "test"},
                "agents_engaged": ["sovereign", "economist"],
                "agent_responses": {
                    "sovereign": {"rating": "ACCEPT", "confidence": 80}
                },
                "final_recommendation": {"recommendation": "Test recommendation"},
                "timestamp": datetime.now(),  # datetime object, not string
                "user_feedback": {"quality_score": 4.0},
                "outcome": {"status": "not_implemented", "alignment_score": 0.0}
            }
            
            case_id = manager.store_case(case)
            assert case_id == case["id"]
            print("✓ Case stored successfully")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_memory_manager_retrieve_similar(self):
        """Test retrieving similar cases."""
        from src.consortium.memory import MemoryManager
        
        temp_dir = tempfile.mkdtemp()
        try:
            manager = MemoryManager(persist_directory=temp_dir)
            
            # Store a test case first
            case = {
                "id": f"test-retrieve-{datetime.now().isoformat()}",
                "query": "Should we use AWS for automotive data?",
                "context": {"industry": "automotive"},
                "agents_engaged": ["sovereign", "economist"],
                "agent_responses": {
                    "sovereign": {"rating": "BLOCK", "confidence": 95}
                },
                "final_recommendation": {"recommendation": "Use EU cloud instead"},
                "timestamp": datetime.now(),
                "user_feedback": {"quality_score": 4.5},
                "outcome": {"status": "not_implemented", "alignment_score": 0.0}
            }
            manager.store_case(case)
            
            # Retrieve similar cases - note: no 'context' parameter
            results = manager.retrieve_similar_cases(
                query="automotive cloud migration",
                top_k=3
            )
            
            assert isinstance(results, dict)
            assert "cases" in results
            assert "retrieval_metadata" in results
            assert isinstance(results["cases"], list)
            print(f"✓ Retrieved {len(results['cases'])} case(s)")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestMemoryManagerIntegration:
    """Integration tests with real ChromaDB."""
    
    def test_memory_manager_with_real_chromadb(self):
        """Test MemoryManager with actual ChromaDB instance."""
        from src.consortium.memory import MemoryManager
        
        temp_dir = tempfile.mkdtemp()
        try:
            manager = MemoryManager(persist_directory=temp_dir)
            
            # Verify collection name matches what we set
            assert manager.collection.name == "strategic_cases"
            
            # Store and retrieve
            case = {
                "id": f"integration-test-{datetime.now().isoformat()}",
                "query": "Integration test query",
                "context": {},
                "agents_engaged": ["sovereign"],
                "agent_responses": {},
                "final_recommendation": {},
                "timestamp": datetime.now(),
                "user_feedback": {"quality_score": 4.0},
                "outcome": {"status": "not_implemented", "alignment_score": 0.0}
            }
            
            case_id = manager.store_case(case)
            assert case_id is not None
            
            # Count cases
            count = manager.count_cases()
            assert count >= 1
            
            print(f"✓ ChromaDB integration works ({count} case(s) stored)")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
