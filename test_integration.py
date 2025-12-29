"""Quick integration test."""
from src.consortium.graph import create_consortium_graph
from src.consortium.state import create_initial_state

graph = create_consortium_graph()
state = create_initial_state(
    query='Should we migrate German automotive data to AWS?',
    context={'industry': 'automotive', 'data_type': 'trade_secrets'}
)

print('Running graph...')
result = graph.invoke(state, {'recursion_limit': 20})

print('\nResults:')
for agent_id, resp in result.get('agent_responses', {}).items():
    print(f'  {agent_id}: {resp.get("rating")} ({resp.get("confidence")}%)')

print(f'\nConverged: {result.get("convergence_status", {}).get("converged")}')

if result.get('final_recommendation'):
    rec = result['final_recommendation'].get('recommendation', '')[:200]
    print(f'\nRecommendation: {rec}...')
