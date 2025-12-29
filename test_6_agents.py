"""Quick integration test with all 6 agents."""
from src.consortium.graph import create_consortium_graph
from src.consortium.state import create_initial_state

graph = create_consortium_graph()
state = create_initial_state(
    query='Build a pan-European AI training platform',
    context={'scale': 'large', 'compute': 'GPU clusters'}
)

print('Running with 6 agents...')
result = graph.invoke(state, {'recursion_limit': 25})

print('\nAgent Responses:')
for agent_id, resp in result.get('agent_responses', {}).items():
    rating = resp.get("rating", "N/A")
    conf = resp.get("confidence", 0)
    print(f'  {agent_id}: {rating} ({conf}%)')

print(f'\nTotal agents: {len(result.get("agent_responses", {}))}')
print(f'Converged: {result.get("convergence_status", {}).get("converged")}')

if result.get('final_recommendation'):
    rec = result['final_recommendation'].get('recommendation', '')[:150]
    print(f'\nRecommendation preview: {rec}...')
