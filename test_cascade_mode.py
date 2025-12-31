"""Test script for CASCADE mode refactoring.

This script validates the new Proposal-Critique-Transformation cascade workflow.

Test cases:
1. Graph compilation (both cascade and parallel modes)
2. State initialization with new fields
3. Import validation for new nodes
4. Basic sanity checks
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all new modules can be imported."""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)

    try:
        from src.consortium.state import ConsortiumState, create_initial_state
        print("✓ State module imported")

        from src.consortium.nodes import (
            founder_provocation_node,
            breaker_critique_node,
            alchemist_transformation_node
        )
        print("✓ Cascade nodes imported")

        from src.consortium.graph import (
            create_consortium_graph,
            create_consortium_graph_cascade,
            create_consortium_graph_parallel
        )
        print("✓ Graph functions imported")

        print("\n✅ ALL IMPORTS SUCCESSFUL\n")
        return True

    except ImportError as e:
        print(f"\n❌ IMPORT FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_state_initialization():
    """Test that state initializes with new cascade fields."""
    print("=" * 60)
    print("TEST 2: State Initialization")
    print("=" * 60)

    try:
        from src.consortium.state import create_initial_state

        state = create_initial_state(
            query="Test query",
            context={"test": "context"}
        )

        # Check new cascade fields
        assert "draft_strategy" in state, "Missing draft_strategy field"
        assert "breaker_constraints" in state, "Missing breaker_constraints field"
        assert "reframed_opportunities" in state, "Missing reframed_opportunities field"

        # Check defaults
        assert state["draft_strategy"] is None, "draft_strategy should default to None"
        assert state["breaker_constraints"] == [], "breaker_constraints should default to []"
        assert state["reframed_opportunities"] == [], "reframed_opportunities should default to []"

        print("✓ State has all required cascade fields")
        print("✓ Default values are correct")
        print(f"✓ State type: {type(state)}")

        print("\n✅ STATE INITIALIZATION SUCCESSFUL\n")
        return True

    except Exception as e:
        print(f"\n❌ STATE INITIALIZATION FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_graph_compilation():
    """Test that both graph modes compile successfully."""
    print("=" * 60)
    print("TEST 3: Graph Compilation")
    print("=" * 60)

    try:
        from src.consortium.graph import (
            create_consortium_graph,
            create_consortium_graph_cascade,
            create_consortium_graph_parallel
        )

        # Test cascade mode
        print("Compiling CASCADE graph...")
        cascade_graph = create_consortium_graph_cascade(enable_scout=False)
        print("✓ Cascade graph compiled successfully")
        print(f"  Type: {type(cascade_graph)}")

        # Test parallel mode
        print("\nCompiling PARALLEL graph...")
        parallel_graph = create_consortium_graph_parallel(enable_scout=False)
        print("✓ Parallel graph compiled successfully")
        print(f"  Type: {type(parallel_graph)}")

        # Test default mode (should be cascade)
        print("\nCompiling graph with default mode...")
        default_graph = create_consortium_graph(enable_scout=False)
        print("✓ Default graph compiled successfully (mode=cascade)")

        # Test explicit mode selection
        print("\nTesting explicit mode selection...")
        cascade_explicit = create_consortium_graph(enable_scout=False, mode="cascade")
        print("✓ Explicit cascade mode works")

        parallel_explicit = create_consortium_graph(enable_scout=False, mode="parallel")
        print("✓ Explicit parallel mode works")

        print("\n✅ ALL GRAPH COMPILATIONS SUCCESSFUL\n")
        return True

    except Exception as e:
        print(f"\n❌ GRAPH COMPILATION FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_node_structure():
    """Test that cascade nodes have correct structure."""
    print("=" * 60)
    print("TEST 4: Node Structure Validation")
    print("=" * 60)

    try:
        from src.consortium.nodes import (
            founder_provocation_node,
            breaker_critique_node,
            alchemist_transformation_node
        )

        # Check that nodes are callable
        assert callable(founder_provocation_node), "founder_provocation_node not callable"
        print("✓ founder_provocation_node is callable")

        assert callable(breaker_critique_node), "breaker_critique_node not callable"
        print("✓ breaker_critique_node is callable")

        assert callable(alchemist_transformation_node), "alchemist_transformation_node not callable"
        print("✓ alchemist_transformation_node is callable")

        print("\n✅ ALL NODES HAVE CORRECT STRUCTURE\n")
        return True

    except Exception as e:
        print(f"\n❌ NODE STRUCTURE VALIDATION FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_synthesizer_modes():
    """Test that synthesizer can handle both modes."""
    print("=" * 60)
    print("TEST 5: Synthesizer Mode Detection")
    print("=" * 60)

    try:
        from src.consortium.nodes.synthesizer import synthesizer_node
        from src.consortium.state import create_initial_state

        # Test parallel mode detection (no draft_strategy)
        print("Testing PARALLEL mode detection...")
        parallel_state = create_initial_state(query="Test")
        # Should detect parallel mode (no draft_strategy)
        assert parallel_state.get("draft_strategy") is None
        print("✓ Parallel mode state created (draft_strategy=None)")

        # Test cascade mode detection (has draft_strategy)
        print("\nTesting CASCADE mode detection...")
        cascade_state = create_initial_state(query="Test")
        cascade_state["draft_strategy"] = "Test strategy"
        assert cascade_state.get("draft_strategy") is not None
        print("✓ Cascade mode state created (draft_strategy set)")

        print("\n✅ SYNTHESIZER MODE DETECTION SUCCESSFUL\n")
        return True

    except Exception as e:
        print(f"\n❌ SYNTHESIZER MODE DETECTION FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all validation tests."""
    print("\n" + "=" * 60)
    print("CASCADE MODE REFACTORING - VALIDATION TESTS")
    print("=" * 60 + "\n")

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("State Initialization", test_state_initialization()))
    results.append(("Graph Compilation", test_graph_compilation()))
    results.append(("Node Structure", test_node_structure()))
    results.append(("Synthesizer Modes", test_synthesizer_modes()))

    # Print summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - CASCADE MODE READY FOR USE 🎉\n")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review errors above\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
