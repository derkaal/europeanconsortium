"""Demonstration of the consortium graph with real node logic."""

from src.consortium import create_consortium_graph, create_initial_state
import json


def main():
    """Run a demonstration of the consortium graph."""
    print("=" * 80)
    print("EUROPEAN STRATEGY CONSORTIUM - ITERATION 5 DEMO")
    print("=" * 80)
    print()
    
    # Create the graph
    print("Creating consortium graph...")
    graph = create_consortium_graph()
    print("✓ Graph compiled successfully")
    print()
    
    # Create initial state
    query = "Should the EU invest €500M in renewable energy infrastructure?"
    context = {
        "budget": 500_000_000,
        "timeframe": "5 years",
        "region": "European Union"
    }
    
    print(f"Query: {query}")
    print(f"Context: {json.dumps(context, indent=2)}")
    print()
    
    # Run the graph
    print("Running graph...")
    initial_state = create_initial_state(query=query, context=context)
    result = graph.invoke(initial_state)
    print("✓ Graph execution completed")
    print()
    
    # Display results
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    
    print(f"Triggered Agents: {', '.join(result['triggered_agents'])}")
    print()
    
    print("Agent Responses:")
    for agent_id, response in result["agent_responses"].items():
        confidence_pct = response['confidence'] * 100
        print(f"  • {agent_id.upper()}")
        print(f"    Rating: {response['rating']}")
        print(f"    Confidence: {confidence_pct:.0f}%")
        print(f"    Reasoning: {response['reasoning'][:150]}...")
        if response.get('mitigation_plan'):
            print(f"    Mitigation: {response['mitigation_plan'][:100]}...")
        print()
    
    # Convergence status
    conv = result['convergence_status']
    print("Convergence Status:")
    print(f"  Converged: {conv['converged']}")
    print(f"  Reason: {conv['reason']}")
    if 'avg_confidence' in conv:
        print(f"  Avg Confidence: {conv['avg_confidence']:.1f}%")
    if 'positive_percentage' in conv:
        print(f"  Agreement: {conv['positive_percentage']:.1f}%")
    print()
    
    # Final recommendation
    rec = result['final_recommendation']
    print("=" * 80)
    print("FINAL RECOMMENDATION")
    print("=" * 80)
    print()
    print(rec['recommendation'])
    print()
    
    if rec.get('action_items'):
        print("Action Items:")
        for item in rec['action_items']:
            print(f"  [{item['priority']}] {item['action']}")
            print(f"      Owner: {item['owner']}")
            print(f"      Details: {item['details']}")
            print()
    
    print("=" * 80)
    print("IMPLEMENTATION STATUS")
    print("=" * 80)
    print()
    print("✅ Graph structure with 6 nodes")
    print("✅ Conditional routing with Literal type hints")
    print("✅ Real convergence testing (4 criteria)")
    print("✅ Pyramid Principle synthesis")
    print("✅ Proper state management with reducers")
    print()
    print("📝 Using mock agent responses (real LLM integration pending)")
    print("📝 Tension detection/resolution stubs (orchestrator pending)")
    print()


if __name__ == "__main__":
    main()
