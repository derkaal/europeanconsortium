"""Diagnostic script to test graph execution."""
import logging
from src.consortium.graph import create_consortium_graph
from src.consortium.state import create_initial_state

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(name)s - %(message)s')

print("=" * 60)
print("GRAPH DIAGNOSTIC TEST")
print("=" * 60)

try:
    print("\n1. Creating graph...")
    graph = create_consortium_graph()
    print("✓ Graph created successfully")
    
    print("\n2. Creating initial state...")
    state = create_initial_state(
        query='Should we use AWS for European data?',
        context={'industry': 'fintech', 'test': True}
    )
    print(f"✓ Initial state created")
    print(f"  - Query: {state['query']}")
    print(f"  - Triggered agents: {state.get('triggered_agents', [])}")
    
    print("\n3. Invoking graph (recursion_limit=25)...")
    result = graph.invoke(state, {'recursion_limit': 25})
    
    print("\n" + "=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    
    print(f"\n4. Results:")
    print(f"  - Agent responses: {len(result.get('agent_responses', {}))} agents")
    for agent_id, response in result.get('agent_responses', {}).items():
        print(f"    • {agent_id}: {response.get('rating', 'N/A')} ({response.get('confidence', 0)}%)")
    
    convergence = result.get('convergence_status', {})
    print(f"\n  - Convergence: {convergence.get('converged', False)}")
    if convergence:
        print(f"    Reason: {convergence.get('reason', 'N/A')}")
    
    if result.get('final_recommendation'):
        rec = result['final_recommendation'].get('recommendation', 'N/A')
        print(f"\n  - Recommendation: {rec[:200]}...")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("ERROR!")
    print("=" * 60)
    print(f"\nException: {type(e).__name__}")
    print(f"Message: {str(e)}")
    
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
