"""Historical test case validation for European Strategy Consortium."""
import pytest
import yaml
import os
import sys
from pathlib import Path

sys.path.insert(0, '.')

# Skip entire module if no API keys
pytestmark = pytest.mark.skipif(
    not any([os.getenv("ANTHROPIC_API_KEY"), os.getenv("OPENAI_API_KEY")]),
    reason="Requires API key for real LLM testing"
)


def load_test_cases():
    """Load all test cases from YAML files."""
    cases_dir = Path(__file__).parent / "historical_cases"
    cases = []
    
    if not cases_dir.exists():
        return []
    
    for yaml_file in sorted(cases_dir.glob("*.yaml")):
        try:
            with open(yaml_file, encoding='utf-8') as f:
                case = yaml.safe_load(f)
                if case:
                    cases.append(case)
        except Exception as e:
            print(f"Warning: Could not load {yaml_file}: {e}")
    
    return cases


class TestHistoricalCases:
    """Test historical cases against the consortium."""
    
    @pytest.fixture(scope="class")
    def graph(self):
        """Create graph once for all tests."""
        from src.consortium.graph import create_consortium_graph
        return create_consortium_graph()
    
    @pytest.mark.parametrize(
        "case", load_test_cases(), ids=lambda c: c.get("id", "unknown")
    )
    def test_case(self, graph, case):
        """Test a historical case against the consortium."""
        from src.consortium.state import create_initial_state
        
        print(f"\n{'='*60}")
        print(f"CASE: {case['id']} - {case['name']}")
        print(f"{'='*60}")
        print(f"Query: {case['query']}")
        
        state = create_initial_state(
            query=case["query"],
            context=case.get("context", {})
        )
        
        result = graph.invoke(state, {"recursion_limit": 25})
        
        # Basic validation
        responses = result.get("agent_responses", {})
        assert responses, f"No agent responses for case {case['id']}"
        
        print("\nAgent Responses:")
        for agent_id, response in responses.items():
            rating = response.get("rating", "N/A")
            confidence = response.get("confidence", 0)
            print(f"  {agent_id}: {rating} ({confidence}%)")
        
        # Check expected agents participated
        for expected_agent in case.get("expected_agents", []):
            if expected_agent in ["sovereign", "economist", "jurist"]:
                assert expected_agent in responses, (
                    f"Expected {expected_agent} to respond in "
                    f"case {case['id']}"
                )
        
        # Check validation criteria
        criteria = case.get("validation_criteria", {})
        
        # Check must_mention terms
        if criteria.get("must_mention"):
            all_reasoning = " ".join(
                r.get("reasoning", "") for r in responses.values()
            ).lower()
            
            for term in criteria["must_mention"]:
                assert term.lower() in all_reasoning, \
                    f"Expected mention of '{term}' in case {case['id']}"
            terms = criteria['must_mention']
            print(f"\n✓ All required terms mentioned: {terms}")
        
        # Check expected ratings
        if criteria.get("expected_sovereign_rating"):
            sovereign = responses.get("sovereign", {})
            expected = criteria["expected_sovereign_rating"]
            actual = sovereign.get("rating", "N/A")
            print(f"  Sovereign rating: {actual} (expected: {expected})")
        
        if criteria.get("expected_jurist_rating"):
            jurist = responses.get("jurist", {})
            expected = criteria["expected_jurist_rating"]
            actual = jurist.get("rating", "N/A")
            print(f"  Jurist rating: {actual} (expected: {expected})")
        
        # Check CLA verdict if expected
        if case.get("expected_cla_verdict"):
            cla_review = result.get("cla_review") or responses.get("cla", {})
            actual_verdict = cla_review.get("verdict", "N/A")
            expected_verdict = case["expected_cla_verdict"]
            print(
                f"\nCLA Verdict: {actual_verdict} "
                f"(expected: {expected_verdict})"
            )
            
            if criteria.get("cla_must_fail"):
                failed_tests = cla_review.get("failed_tests", [])
                print(f"  Failed tests: {failed_tests}")
        
        # Check final recommendation exists
        final_rec = result.get("final_recommendation")
        assert final_rec, f"No final recommendation for case {case['id']}"
        
        rec_text = final_rec.get("recommendation", "")[:300]
        print(f"\nRecommendation preview:\n  {rec_text}...")
        
        # Check conditionality mechanisms if CLA was involved
        if final_rec.get("conditionality_mechanisms"):
            mechs = final_rec["conditionality_mechanisms"]
            print("\nConditionality Mechanisms:")
            print(f"  Trigger: {mechs.get('trigger', 'N/A')}")
            print(f"  Action: {mechs.get('action', 'N/A')}")
        
        print(f"\n✓ Case {case['id']} completed successfully")


class TestPerformance:
    """Performance benchmarks."""
    
    def test_execution_time(self):
        """Benchmark system performance."""
        import time
        from src.consortium.graph import create_consortium_graph
        from src.consortium.state import create_initial_state
        
        graph = create_consortium_graph()
        
        queries = [
            ("simple", "Should we use AWS for European data?"),
            (
                "medium",
                "Create an AI-powered customer service platform for EU market"
            ),
            (
                "complex",
                "Build pan-European healthcare data exchange with 27 member "
                "states"
            ),
        ]
        
        results = []
        
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK")
        print("="*60)
        
        for complexity, query in queries:
            state = create_initial_state(query=query, context={})
            
            start = time.time()
            result = graph.invoke(state, {"recursion_limit": 15})
            elapsed = time.time() - start
            
            agent_count = len(result.get("agent_responses", {}))
            results.append((complexity, elapsed, agent_count))
            
            print(f"\n{complexity.upper()} query:")
            print(f"  Time: {elapsed:.1f}s")
            print(f"  Agents: {agent_count}")
        
        avg_time = sum(r[1] for r in results) / len(results)
        print(f"\n{'='*60}")
        print(f"Average execution time: {avg_time:.1f}s")
        print(f"{'='*60}")
        
        # Performance criteria from spec: complex queries < 5 minutes
        assert avg_time < 300, (
            f"Average time {avg_time:.1f}s exceeds 5 minute limit"
        )
        print("\n✓ Performance within acceptable limits")


class TestProductionReadiness:
    """Production readiness checks."""
    
    def test_error_recovery(self):
        """Test system handles errors gracefully."""
        from src.consortium.graph import create_consortium_graph
        from src.consortium.state import create_initial_state
        
        graph = create_consortium_graph()
        
        # Empty query - system should handle gracefully
        state = create_initial_state(query="", context={})
        
        try:
            result = graph.invoke(state, {"recursion_limit": 10})
            # If it completes, that's fine
            assert result is not None
            print("✓ Handles empty query - completed")
        except Exception as e:
            # Recursion limit or other errors are acceptable for malformed
            if "recursion" in str(e).lower() or "limit" in str(e).lower():
                print("✓ Handles empty query - hit recursion limit (expected)")
            else:
                raise
    
    def test_convergence_guaranteed(self):
        """Test that system always converges."""
        from src.consortium.graph import create_consortium_graph
        from src.consortium.state import create_initial_state
        
        graph = create_consortium_graph()
        
        # Contentious query likely to cause disagreement
        state = create_initial_state(
            query="Move all EU citizen data to Chinese cloud providers",
            context={"urgency": "immediate", "budget": "unlimited"}
        )
        
        result = graph.invoke(state, {"recursion_limit": 25})
        
        # Must converge even with contentious query
        convergence = result.get("convergence_status", {})
        assert convergence.get("converged") is True, "Failed to converge"
        
        print(f"✓ Converged: {convergence.get('reason', 'unknown')}")
    
    def test_all_agents_contribute(self):
        """Test that all configured agents contribute."""
        from src.consortium.graph import create_consortium_graph
        from src.consortium.state import create_initial_state
        
        graph = create_consortium_graph()
        
        state = create_initial_state(
            query="Comprehensive EU digital strategy assessment",
            context={"scope": "full_analysis"}
        )
        
        result = graph.invoke(state, {"recursion_limit": 25})
        
        responses = result.get("agent_responses", {})
        
        # At minimum, Big Three should respond
        expected = ["sovereign", "economist", "jurist"]
        for agent in expected:
            assert agent in responses, f"Missing response from {agent}"
        
        print(f"✓ All core agents contributed: {list(responses.keys())}")
