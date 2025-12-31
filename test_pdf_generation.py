"""
Test script for new structured PDF generation.

Generates a sample PDF report to verify the new structure works correctly.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app.pdf_export import generate_consortium_pdf, PDF_AVAILABLE

def create_sample_data():
    """Create sample data for PDF generation test."""

    query = "Should we adopt AWS for our European fintech operations?"

    context = {
        'industry': 'Financial Services',
        'company_size': 'Medium (500-1000 employees)',
        'markets': ['Germany', 'France', 'Netherlands'],
        'constraints': 'Must comply with GDPR and financial regulations'
    }

    agent_responses = {
        'sovereign': {
            'rating': 'WARN',
            'confidence': 0.75,
            'reasoning': 'AWS provides EU regions but US-based parent company creates jurisdiction risks. Data sovereignty concerns regarding CLOUD Act and potential US government access to EU data.',
            'attack_vector': 'CLOUD Act allows US authorities to request data from AWS even when stored in EU regions',
            'mitigation_plan': 'Use AWS EU regions exclusively, implement client-side encryption with EU-based key management'
        },
        'intelligence_sovereign': {
            'rating': 'WARN',
            'confidence': 0.80,
            'reasoning': 'Sending strategic business data to US cloud provider could expose competitive intelligence to foreign jurisdiction.',
            'attack_vector': 'AI/ML training data and business analytics could be accessed by US-based AWS engineers',
            'mitigation_plan': 'Avoid AWS AI services for sensitive data, use on-premise ML for strategic intelligence'
        },
        'economist': {
            'rating': 'ACCEPT',
            'confidence': 0.85,
            'reasoning': 'AWS provides strong feature subsidies through managed services. Cost-effective for startups and scale-ups due to pay-as-you-go model.',
            'mitigation_plan': 'Implement cost monitoring and reserved instances for predictable workloads'
        },
        'jurist': {
            'rating': 'WARN',
            'confidence': 0.70,
            'reasoning': 'Standard Contractual Clauses (SCCs) required for data transfer. Recent Schrems II ruling creates legal uncertainty.',
            'attack_vector': 'Potential invalidation of SCCs could make AWS usage non-compliant with GDPR',
            'mitigation_plan': 'Ensure SCCs are in place, monitor ECJ rulings, have exit strategy ready'
        },
        'architect': {
            'rating': 'ENDORSE',
            'confidence': 0.90,
            'reasoning': 'AWS provides robust architecture options with multi-AZ deployments, good disaster recovery capabilities.',
            'mitigation_plan': 'Design multi-region architecture for critical services'
        },
        'technologist': {
            'rating': 'ACCEPT',
            'confidence': 0.85,
            'reasoning': 'AWS security controls are mature. KMS for encryption, IAM for access control, CloudTrail for auditing.',
            'mitigation_plan': 'Implement client-side encryption, use AWS KMS with customer-managed keys'
        },
        'ecosystem': {
            'rating': 'WARN',
            'confidence': 0.65,
            'reasoning': 'AWS has mixed sustainability record. Some renewable energy commitments but significant carbon footprint.',
            'mitigation_plan': 'Choose EU regions with renewable energy focus (Frankfurt, Ireland)'
        },
        'philosopher': {
            'rating': 'ACCEPT',
            'confidence': 0.75,
            'reasoning': 'AWS provides user control and transparency tools. Ethical concerns about labor practices but not blocking.',
            'mitigation_plan': 'Ensure data handling practices respect user autonomy and dignity'
        },
        'ethnographer': {
            'rating': 'ACCEPT',
            'confidence': 0.80,
            'reasoning': 'AWS has local presence in EU markets, supports works council engagement.',
            'mitigation_plan': 'Ensure proper consultation with works councils before migration'
        },
        'consumer_voice': {
            'rating': 'WARN',
            'confidence': 0.70,
            'reasoning': 'User data protection concerns with US-based provider. Transparency requirements under GDPR.',
            'attack_vector': 'Users may not understand their data is processed by US company',
            'mitigation_plan': 'Provide clear privacy notices about cloud provider and data location'
        },
        'alchemist': {
            'rating': 'ENDORSE',
            'confidence': 0.85,
            'reasoning': 'GDPR compliance can be transmuted into competitive advantage. AWS managed services reduce compliance burden.',
            'mitigation_plan': 'Market GDPR compliance as trust differentiator'
        },
        'founder': {
            'rating': 'ENDORSE',
            'confidence': 0.90,
            'reasoning': 'AWS feature subsidies provide significant cost savings. Managed services accelerate time-to-market.',
            'mitigation_plan': 'Leverage AWS startup credits and feature subsidies for rapid scaling'
        }
    }

    tensions = [
        {
            'agents': 'Sovereign vs. Economist',
            'description': 'Sovereign raises data sovereignty concerns while Economist emphasizes cost benefits',
            'resolution': 'Use AWS EU regions with client-side encryption to balance cost efficiency with sovereignty requirements'
        },
        {
            'agents': 'Intelligence Sovereign vs. Alchemist',
            'description': 'Intelligence Sovereign concerned about strategic data exposure while Alchemist sees opportunity',
            'resolution': 'Segment data: use AWS for non-strategic workloads, keep strategic intelligence on-premise'
        }
    ]

    final_recommendation = {
        'recommendation': 'RECOMMENDED WITH CONDITIONS (Confidence: 78%)\n\n'
                         'The consortium recommends adopting AWS for European fintech operations with specific conditions to address data sovereignty, legal compliance, and sustainability concerns. While AWS provides strong technical capabilities and cost benefits through feature subsidies, the US jurisdiction creates risks that must be mitigated through architectural and contractual safeguards.',
        'supporting_arguments': agent_responses,
        'action_items': [
            {
                'action': 'Implement Standard Contractual Clauses (SCCs) with AWS',
                'owner': 'Legal Team',
                'priority': 'CRITICAL',
                'details': 'Ensure all data processing agreements include valid SCCs per Schrems II requirements. Monitor ECJ rulings for changes to SCC validity.'
            },
            {
                'action': 'Configure client-side encryption with EU-based key management',
                'owner': 'Security Team',
                'priority': 'CRITICAL',
                'details': 'Implement encryption before data reaches AWS. Use AWS KMS with customer-managed keys stored in EU regions, or use third-party EU-based key management service.'
            },
            {
                'action': 'Restrict all infrastructure to AWS EU regions',
                'owner': 'Infrastructure Team',
                'priority': 'CRITICAL',
                'details': 'Use only Frankfurt, Ireland, Paris, Stockholm, or Milan regions. Implement service control policies to prevent accidental US region usage.'
            },
            {
                'action': 'Conduct works council consultation',
                'owner': 'HR Team',
                'priority': 'HIGH',
                'details': 'Engage works councils in Germany, France, and Netherlands before migration. Provide transparency about data processing and employee monitoring implications.'
            },
            {
                'action': 'Develop exit strategy and data portability plan',
                'owner': 'Strategy Team',
                'priority': 'HIGH',
                'details': 'Document procedure for migrating away from AWS if SCCs are invalidated or sovereignty requirements change. Ensure data portability through standard formats.'
            },
            {
                'action': 'Implement cost monitoring and optimization',
                'owner': 'Finance Team',
                'priority': 'MEDIUM',
                'details': 'Set up AWS Cost Explorer, implement tagging strategy, use reserved instances for predictable workloads.'
            },
            {
                'action': 'Update privacy notices for customers',
                'owner': 'Legal/Product Team',
                'priority': 'MEDIUM',
                'details': 'Provide clear information about AWS as data processor, data location, and international transfers in privacy policy.'
            },
            {
                'action': 'Choose renewable energy focused AWS regions',
                'owner': 'Infrastructure Team',
                'priority': 'LOW',
                'details': 'Prioritize Frankfurt and Ireland regions which have stronger renewable energy commitments.'
            }
        ],
        'decision_provenance': {
            'query': query,
            'agents_engaged': list(agent_responses.keys()),
            'tensions_detected': len(tensions),
            'iteration_count': 2
        },
        'competitive_advantages': {
            'regulatory_moats': [
                'GDPR compliance as trust differentiator',
                'Strong data protection as competitive advantage in EU market'
            ]
        }
    }

    convergence_status = {
        'converged': True,
        'positive_percentage': 75,
        'iteration_count': 2,
        'gate_status': {
            'block_count': 0,
            'warn_count': 5,
            'avg_confidence': 0.78
        }
    }

    return query, context, agent_responses, tensions, final_recommendation, convergence_status


def main():
    """Run PDF generation test."""
    print("Testing new structured PDF generation...")
    print("=" * 60)

    if not PDF_AVAILABLE:
        print("ERROR: reportlab not installed")
        print("Install with: pip install reportlab")
        return 1

    print("\n1. Creating sample data...")
    query, context, agent_responses, tensions, final_recommendation, convergence_status = create_sample_data()
    print(f"   ✓ Query: {query[:50]}...")
    print(f"   ✓ Agents: {len(agent_responses)}")
    print(f"   ✓ Tensions: {len(tensions)}")
    print(f"   ✓ Action items: {len(final_recommendation['action_items'])}")

    print("\n2. Generating PDF...")
    try:
        pdf_buffer = generate_consortium_pdf(
            query=query,
            context=context,
            agent_responses=agent_responses,
            tensions=tensions,
            final_recommendation=final_recommendation,
            convergence_status=convergence_status
        )
        print("   ✓ PDF generated successfully")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n3. Saving PDF to test_output.pdf...")
    try:
        with open('test_output.pdf', 'wb') as f:
            f.write(pdf_buffer.read())
        print("   ✓ PDF saved successfully")
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return 1

    print("\n" + "=" * 60)
    print("SUCCESS! PDF structure test completed.")
    print("Review test_output.pdf to verify:")
    print("  - Cover page")
    print("  - Table of contents")
    print("  - Executive summary")
    print("  - Recommended solutions")
    print("  - Implementation roadmap")
    print("  - 6 thematic chapters")
    print("  - Appendices (agents, tensions, methodology)")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    exit(main())
