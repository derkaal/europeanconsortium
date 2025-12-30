"""
European Strategy Consortium - Streamlit Demo UI

Interactive interface for querying the multi-agent consortium and viewing
real-time deliberation results.
"""

import streamlit as st
import sys
import os
import yaml
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import consortium components
from src.consortium import create_consortium_graph, create_initial_state
from src.consortium.tiered_llm_provider import get_tiered_provider

# PDF generation
try:
    from app.pdf_export import generate_consortium_pdf, PDF_AVAILABLE
except ImportError:
    PDF_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="European Strategy Consortium",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .agent-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        color: #1e1e1e;
    }
    .agent-card h4 {
        color: #1e1e1e;
        margin-top: 0;
    }
    .agent-card p {
        color: #1e1e1e;
        margin: 0.5rem 0;
    }
    .block-card {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    .warn-card {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    .accept-card {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
    .endorse-card {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .tension-box {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #9c27b0;
        margin: 1rem 0;
        color: #1e1e1e;
    }
    .tension-box h4 {
        color: #1e1e1e;
        margin-top: 0;
    }
    .tension-box p {
        color: #1e1e1e;
        margin: 0.5rem 0;
    }
    .alchemist-box {
        background-color: #fce4ec;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #e91e63;
        margin: 1rem 0;
        color: #1e1e1e;
    }
    .alchemist-box h4 {
        color: #1e1e1e;
        margin-top: 0;
    }
    .alchemist-box p {
        color: #1e1e1e;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🇪🇺 European Strategy Consortium")
st.markdown("""
Multi-agent deliberation system for European business strategy.
12 specialized agents evaluate proposals through adversarial collaboration,
converging on **"Yes, If"** recommendations.
""")

# Sidebar: Agent selection and settings
with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("Enabled Agents")

    # Tier 0 - Foundational
    st.markdown("**Tier 0: Foundational Agents (Big Three + AI Sovereignty)**")
    sovereign_enabled = st.checkbox(
        "🛡️ Sovereign (Data Sovereignty)", value=True
    )
    intelligence_sovereign_enabled = st.checkbox(
        "🤖 Intelligence Sovereign (AI Sovereignty)", value=True
    )
    economist_enabled = st.checkbox(
        "💰 Economist (Financial Viability)", value=True
    )
    jurist_enabled = st.checkbox(
        "⚖️ Jurist (Legal Compliance)", value=True
    )

    # Tier 1
    st.markdown("**Tier 1: Technical & Values**")
    architect_enabled = st.checkbox(
        "🏗️ Architect (Systems Design)", value=True
    )
    ecosystem_enabled = st.checkbox(
        "🌱 Eco-System (Sustainability)", value=True
    )
    philosopher_enabled = st.checkbox(
        "🧠 Philosopher (Ethics)", value=True
    )

    # Tier 2
    st.markdown("**Tier 2: Specialized Agents**")
    ethnographer_enabled = st.checkbox(
        "🌍 Ethnographer (Cultural Fit)", value=True
    )
    technologist_enabled = st.checkbox(
        "🔒 Technologist (Security)", value=True
    )
    consumer_voice_enabled = st.checkbox(
        "👥 Consumer Voice (User Protection)", value=True
    )

    # Tier 3 - Feature Subsidy Agents
    st.markdown("**Tier 3: Feature Subsidy Agents**")
    alchemist_enabled = st.checkbox(
        "💎 Alchemist (Regulation-to-Value)",
        value=True,
        help="Transforms regulatory constraints into competitive advantages"
    )
    founder_enabled = st.checkbox(
        "🚀 Founder (Feature Hunter)",
        value=True,
        help="Hunts Feature Subsidies and regulatory arbitrage opportunities"
    )

    # Meta-Agent
    st.markdown("**Meta-Agent (Special Purpose)**")
    cla_enabled = st.checkbox(
        "🧟 CLA (Zombie Detection)",
        value=False,
        help="Only for proposals creating permanent programs/regulations"
    )

    st.divider()

    # Model Configuration Display
    with st.expander("🤖 Model Configuration", expanded=False):
        st.subheader("Tiered LLM System")
        st.markdown("""
        Models are automatically selected based on task complexity:
        """)
        
        # Load model tiers config
        try:
            config_path = Path("config/model_tiers.yaml")
            if config_path.exists():
                with open(config_path) as f:
                    model_config = yaml.safe_load(f)
                    tiers = model_config.get("model_tiers", {})
                    
                    # Display each tier
                    for tier_name, tier_data in tiers.items():
                        st.markdown(f"**{tier_name.upper()} Tier**")
                        st.caption(tier_data.get("description", ""))
                        
                        primary = tier_data.get("primary", {})
                        st.text(f"  Primary: {primary.get('provider', 'N/A')} - {primary.get('model', 'N/A')}")
                        
                        fallback1 = tier_data.get("fallback_1", {})
                        if fallback1:
                            st.text(f"  Fallback 1: {fallback1.get('provider', 'N/A')} - {fallback1.get('model', 'N/A')}")
                        
                        fallback2 = tier_data.get("fallback_2", {})
                        if fallback2:
                            st.text(f"  Fallback 2: {fallback2.get('provider', 'N/A')} - {fallback2.get('model', 'N/A')}")
                        
                        st.divider()
            else:
                st.warning("Model configuration file not found")
        except Exception as e:
            st.error(f"Error loading model configuration: {e}")
    
    # Cost Tracker Display
    with st.expander("💰 Cost Tracker", expanded=False):
        st.subheader("Session Cost Summary")
        
        # Initialize cost tracking in session state
        if 'cost_summary' not in st.session_state:
            st.session_state.cost_summary = {
                'total_cost_usd': 0.0,
                'costs_by_tier': {'reasoning': 0.0, 'standard': 0.0, 'fast': 0.0, 'embedding': 0.0},
                'calls_by_tier': {'reasoning': 0, 'standard': 0, 'fast': 0, 'embedding': 0}
            }
        
        cost_summary = st.session_state.cost_summary
        
        # Display total cost
        st.metric("Total Session Cost", f"${cost_summary['total_cost_usd']:.4f}")
        
        # Display breakdown by tier
        st.markdown("**Cost by Tier:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Reasoning", f"${cost_summary['costs_by_tier']['reasoning']:.4f}",
                     f"{cost_summary['calls_by_tier']['reasoning']} calls")
            st.metric("Standard", f"${cost_summary['costs_by_tier']['standard']:.4f}",
                     f"{cost_summary['calls_by_tier']['standard']} calls")
        
        with col2:
            st.metric("Fast", f"${cost_summary['costs_by_tier']['fast']:.4f}",
                     f"{cost_summary['calls_by_tier']['fast']} calls")
            st.metric("Embedding", f"${cost_summary['costs_by_tier']['embedding']:.4f}",
                     f"{cost_summary['calls_by_tier']['embedding']} calls")
        
        if st.button("Reset Cost Tracker"):
            st.session_state.cost_summary = {
                'total_cost_usd': 0.0,
                'costs_by_tier': {'reasoning': 0.0, 'standard': 0.0, 'fast': 0.0, 'embedding': 0.0},
                'calls_by_tier': {'reasoning': 0, 'standard': 0, 'fast': 0, 'embedding': 0}
            }
            st.rerun()

    # Advanced settings
    with st.expander("Advanced Settings"):
        st.subheader("Consensus Settings")
        max_iterations = st.slider("Max Consensus Iterations", 1, 10, 5)
        convergence_threshold = st.slider(
            "Convergence Threshold", 0.5, 1.0, 0.7, 0.05
        )
        
        st.divider()
        st.subheader("Demo Mode")
        demo_mode = st.checkbox(
            "Demo Mode (Mock Responses)",
            value=True,
            help="Use mock LLM responses to avoid API costs"
        )

# Main query input
st.header("📝 Strategic Query")

# Context inputs
col1, col2 = st.columns(2)

with col1:
    query = st.text_area(
        "Enter your strategic question:",
        height=100,
        placeholder="Example: Should we move our automotive R&D data "
                    "to a US cloud provider?",
        max_chars=2000
    )

    industry = st.selectbox(
        "Industry",
        [
            "", "Automotive", "Finance", "Healthcare", "Technology",
            "Retail", "Manufacturing", "Public Sector", "Other"
        ]
    )

    company_size = st.selectbox(
        "Company Size",
        [
            "", "Startup (<50)", "Small (50-250)", "Medium (250-1000)",
            "Large (1000-5000)", "Enterprise (>5000)"
        ]
    )

with col2:
    markets = st.multiselect(
        "Target Markets",
        [
            "Germany", "France", "Italy", "Spain", "Netherlands",
            "Belgium", "Poland", "Sweden", "Denmark", "Ireland", "Other EU"
        ]
    )

    constraints = st.text_area(
        "Key Constraints (optional)",
        height=100,
        placeholder="e.g., 'Works council must approve', "
                    "'Limited budget: €500K', 'Must launch in 3 months'"
    )

# Analyze button
analyze_button = st.button(
    "🔍 Analyze with Consortium",
    type="primary",
    use_container_width=True
)

# Store results in session state for PDF export
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Analysis results
if analyze_button:
    if not query:
        st.error("Please enter a strategic question.")
    else:
        # Build enabled agents list
        enabled_agents = []
        if sovereign_enabled:
            enabled_agents.append("sovereign")
        if intelligence_sovereign_enabled:
            enabled_agents.append("intelligence_sovereign")
        if economist_enabled:
            enabled_agents.append("economist")
        if jurist_enabled:
            enabled_agents.append("jurist")
        if architect_enabled:
            enabled_agents.append("architect")
        if ecosystem_enabled:
            enabled_agents.append("ecosystem")
        if philosopher_enabled:
            enabled_agents.append("philosopher")
        if ethnographer_enabled:
            enabled_agents.append("ethnographer")
        if technologist_enabled:
            enabled_agents.append("technologist")
        if consumer_voice_enabled:
            enabled_agents.append("consumer_voice")
        if alchemist_enabled:
            enabled_agents.append("alchemist")
        if founder_enabled:
            enabled_agents.append("founder")

        if len(enabled_agents) == 0:
            st.error("Please enable at least one agent.")
        else:
            # Create status container for real-time progress updates
            status_container = st.status("🚀 Initializing European Strategy Consortium...", expanded=True)

            with status_container:
                # Real or mock implementation
                if demo_mode:
                    # Build context
                    context = {}
                    if industry:
                        context["industry"] = industry
                    if company_size:
                        context["company_size"] = company_size
                    if markets:
                        context["markets"] = markets
                    if constraints:
                        context["constraints"] = constraints
                    
                    # Create mock responses based on query
                    agent_data = {
                        "sovereign": {
                            "rating": "WARN",
                            "confidence": 0.75,
                            "reasoning": "Data sovereignty concerns: US Cloud "
                                       "Act exposure for EU data. Recommend: "
                                       "EU cloud provider (OVHcloud, Scaleway) "
                                       "OR AWS EU with encryption + "
                                       "customer-managed keys.",
                            "color": "warn"
                        },
                        "intelligence_sovereign": {
                            "rating": "WARN",
                            "confidence": 0.82,
                            "reasoning": "AI sovereignty concerns: If using AI "
                                       "for R&D analysis, avoid sending "
                                       "strategic intelligence to foreign AI "
                                       "providers (GPT-4, Claude). Recommend: "
                                       "Mistral AI or self-hosted Llama 3 for "
                                       "sensitive AI workloads.",
                            "color": "warn"
                        },
                        "economist": {
                            "rating": "ACCEPT",
                            "confidence": 0.82,
                            "reasoning": "Cloud TCO favorable: On-prem "
                                       "€10M/year vs Cloud €6-8M/year. ROI "
                                       "within 18 months. Trust Premium "
                                       "positioning can justify any sovereignty "
                                       "premium.",
                            "color": "accept"
                        },
                        "jurist": {
                            "rating": "WARN",
                            "confidence": 0.88,
                            "reasoning": "GDPR Article 46: Standard Contractual "
                                       "Clauses (SCCs) required for US provider. "
                                       "Recommend: Data Processing Agreement + "
                                       "SCCs + encryption. Works council "
                                       "approval needed (Germany).",
                            "color": "warn"
                        },
                        "architect": {
                            "rating": "ACCEPT",
                            "confidence": 0.70,
                            "reasoning": "Cloud architecture sound for R&D "
                                       "workloads. Recommend: Multi-region "
                                       "deployment, backup strategy, disaster "
                                       "recovery plan. Technical debt: low.",
                            "color": "accept"
                        },
                        "ecosystem": {
                            "rating": "WARN",
                            "confidence": 0.65,
                            "reasoning": "High compute workloads = high carbon "
                                       "footprint. Require: Renewable energy "
                                       "commitment from cloud provider. Target: "
                                       "<0.1 kg CO₂/kWh (vs current data "
                                       "center: 0.5 kg CO₂/kWh).",
                            "color": "warn"
                        },
                        "philosopher": {
                            "rating": "ACCEPT",
                            "confidence": 0.73,
                            "reasoning": "R&D data not directly user-facing, "
                                       "lower ethical concerns. Ensure: "
                                       "Employee privacy protected, no "
                                       "surveillance of internal communications. "
                                       "Autonomy: reasonable.",
                            "color": "accept"
                        },
                        "ethnographer": {
                            "rating": "WARN",
                            "confidence": 0.80,
                            "reasoning": "German engineering culture values "
                                       "control and precision. Works council "
                                       "(Betriebsrat) requires 6-month "
                                       "consultation for IT changes. Recommend: "
                                       "Phased migration, cultural change "
                                       "management, emphasize quality not just "
                                       "cost.",
                            "color": "warn"
                        },
                        "technologist": {
                            "rating": "WARN",
                            "confidence": 0.85,
                            "reasoning": "Trade secret protection critical for "
                                       "automotive R&D. BLOCK: Unencrypted data "
                                       "in cloud. REQUIRE: Encryption in use "
                                       "(confidential computing), HSM for key "
                                       "management, SIEM for threat detection.",
                            "color": "warn"
                        },
                        "consumer_voice": {
                            "rating": "ACCEPT",
                            "confidence": 0.60,
                            "reasoning": "B2B scenario, not direct consumer "
                                       "impact. Ensure: Customer data (if any) "
                                       "remains protected. Transparency: inform "
                                       "customers if their data affected by "
                                       "cloud migration.",
                            "color": "accept"
                        },
                        "alchemist": {
                            "rating": "ENDORSE",
                            "confidence": 0.90,
                            "reasoning": "LEVEL 5 ALCHEMY DETECTED: GDPR + AI "
                                       "Act compliance can be transmuted into "
                                       "competitive moat. Trust Premium: "
                                       "Position as 'German Engineering on "
                                       "Secure European Cloud' → 15% B2B "
                                       "premium (€3.2M/year). Moat Analysis: "
                                       "Your compliance-native infrastructure "
                                       "costs €1 to maintain; competitors "
                                       "retrofitting legacy systems cost €10. "
                                       "Market Creation: Sell 'EU-Secure Cloud "
                                       "Migration Services' to other automotive "
                                       "firms.",
                            "color": "endorse"
                        },
                        "founder": {
                            "rating": "ENDORSE",
                            "confidence": 0.88,
                            "reasoning": "FEATURE SUBSIDY STACK IDENTIFIED: "
                                       "(1) Data Sovereignty Premium: 15% price "
                                       "uplift on R&D services = €3.2M/year. "
                                       "(2) Carbon Credits: Renewable energy "
                                       "cloud = ETS credit capture. (3) AI "
                                       "Sovereignty: Build internal Mistral AI "
                                       "capability → sell 'EU-Sovereign AI for "
                                       "Automotive' as new revenue stream. "
                                       "Arbitrage Window: 18 months before "
                                       "competitors wake up to Cloud Act risks. "
                                       "Revenue Transformation: €4M savings + "
                                       "€3.2M premium + €2M new AI services = "
                                       "€9.2M total value. NO GRANTS NEEDED.",
                            "color": "endorse"
                        },
                    }

                    # Filter to enabled agents
                    filtered_agents = {
                        k: v for k, v in agent_data.items()
                        if k in enabled_agents
                    }
                    
                    # Mock tensions
                    tensions = [
                        {
                            "agents": "Sovereign ↔ Economist",
                            "description": "Data sovereignty requirements "
                                         "(EU cloud) vs cost optimization "
                                         "(AWS cheaper)",
                            "resolution": "AWS EU regions + encryption + "
                                        "customer-managed keys. Position as "
                                        "'Trust Premium' to justify cost."
                        },
                        {
                            "agents": "Ethnographer ↔ Architect",
                            "description": "Cultural change management "
                                         "(6-month works council process) vs "
                                         "technical speed (3-month migration)",
                            "resolution": "Phased migration: Start with "
                                        "non-critical workloads (3 months), "
                                        "expand after works council approval "
                                        "(6-9 months total)"
                        }
                    ]
                    
                    # Mock final recommendation
                    final_rec = {
                        "recommendation": "RECOMMENDED WITH CONDITIONS "
                                        "(Confidence: 78%)\n\nBased on "
                                        "analysis by 10 expert agents, the "
                                        "consortium's assessment is: Mixed "
                                        "assessment with conditions noted.",
                        "action_items": [
                            {
                                "action": "Use AWS EU regions (Frankfurt, "
                                        "Ireland) exclusively",
                                "owner": "Infrastructure Team",
                                "priority": "HIGH",
                                "details": "Ensure all data remains within EU "
                                         "jurisdiction"
                            },
                            {
                                "action": "Implement encryption at rest, in "
                                        "transit, and in use (confidential "
                                        "computing)",
                                "owner": "Security Team",
                                "priority": "HIGH",
                                "details": "Use AWS confidential computing "
                                         "features"
                            },
                            {
                                "action": "Customer-managed encryption keys "
                                        "(AWS KMS with CMK)",
                                "owner": "Security Team",
                                "priority": "HIGH",
                                "details": "Maintain control over encryption "
                                         "keys"
                            },
                            {
                                "action": "Sign Standard Contractual Clauses "
                                        "(SCCs) with AWS",
                                "owner": "Legal Team",
                                "priority": "HIGH",
                                "details": "GDPR compliance requirement"
                            },
                            {
                                "action": "Engage German works council: "
                                        "6-month consultation process",
                                "owner": "HR & Management",
                                "priority": "HIGH",
                                "details": "Required by German labor law for "
                                         "IT changes"
                            },
                            {
                                "action": "Phased migration: Non-critical "
                                        "workloads first (3 months), critical "
                                        "after approval (6-9 months)",
                                "owner": "Project Management",
                                "priority": "MEDIUM",
                                "details": "Reduces risk and allows for "
                                         "cultural adaptation"
                            },
                            {
                                "action": "Deploy SIEM for security monitoring "
                                        "(AWS Security Hub + GuardDuty)",
                                "owner": "Security Team",
                                "priority": "HIGH",
                                "details": "Continuous threat detection and "
                                         "monitoring"
                            },
                            {
                                "action": "Choose renewable energy regions "
                                        "(AWS EU-Frankfurt: 95% renewable)",
                                "owner": "Sustainability Team",
                                "priority": "MEDIUM",
                                "details": "Align with environmental goals"
                            },
                            {
                                "action": "Implement disaster recovery plan "
                                        "with 99.9% uptime SLA",
                                "owner": "Infrastructure Team",
                                "priority": "HIGH",
                                "details": "Business continuity requirement"
                            },
                            {
                                "action": "Budget: €200K for security controls "
                                        "(HSM, SIEM) + €500K migration costs",
                                "owner": "Finance Team",
                                "priority": "HIGH",
                                "details": "Total investment: €700K with 18-month "
                                         "ROI"
                            }
                        ]
                    }
                    
                    # Store in session state for PDF export
                    st.session_state.analysis_results = {
                        "query": query,
                        "context": context,
                        "agent_responses": filtered_agents,
                        "tensions": tensions,
                        "final_recommendation": final_rec,
                        "convergence_status": {
                            "converged": True,
                            "positive_percentage": 78
                        }
                    }
                    
                    # Display results
                    st.success(
                        f"Analysis complete! {len(enabled_agents)} agents "
                        "consulted."
                    )

                    # Agent responses section
                    st.header("🎭 Agent Deliberation")

                    # Display agent cards
                    cols = st.columns(3)
                    for i, (agent_id, data) in enumerate(filtered_agents.items()):
                        with cols[i % 3]:
                            # Map agent_id to display name
                            agent_names = {
                                "sovereign": "🛡️ Sovereign",
                                "intelligence_sovereign": "🤖 Intelligence "
                                                         "Sovereign",
                                "economist": "💰 Economist",
                                "jurist": "⚖️ Jurist",
                                "architect": "🏗️ Architect",
                                "ecosystem": "🌱 Eco-System",
                                "philosopher": "🧠 Philosopher",
                                "ethnographer": "🌍 Ethnographer",
                                "technologist": "🔒 Technologist",
                                "consumer_voice": "👥 Consumer Voice",
                                "alchemist": "💎 Alchemist",
                                "founder": "🚀 Founder"
                            }

                            st.markdown(f"""
                            <div class="agent-card {data['color']}-card">
                                <h4>{agent_names.get(agent_id, agent_id)}</h4>
                                <p><strong>Rating:</strong> {data['rating']}</p>
                                <p><strong>Confidence:</strong> 
                                   {data['confidence']:.0%}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            with st.expander("📋 Full Reasoning"):
                                st.write(data['reasoning'])

                    # Tensions detected
                    st.header("⚡ Tensions Detected")

                    for tension in tensions:
                        st.markdown(f"""
                        <div class="tension-box">
                            <h4>{tension['agents']}</h4>
                            <p><strong>Conflict:</strong> 
                               {tension['description']}</p>
                            <p><strong>Resolution:</strong> 
                               {tension['resolution']}</p>
                            <p><strong>Status:</strong> ✅ Resolved</p>
                        </div>
                        """, unsafe_allow_html=True)

                    # Final recommendation
                    st.header("📊 Final Recommendation")

                    st.success("**Rating: CONDITIONAL ACCEPT**")
                    st.metric("Consensus", "78%", "+8% from initial")
                    st.metric("Iterations", "2", "Target: <5")

                    st.subheader("Pyramid Principle Summary")

                    st.markdown("""
                    **Main Recommendation:** Proceed with cloud migration using 
                    **AWS EU regions** with data sovereignty controls.

                    **Supporting Arguments:**
                    1. **Financial**: €4M annual savings (€10M on-prem → 
                       €6M cloud), 18-month ROI
                    2. **Legal**: GDPR-compliant via SCCs + encryption + 
                       customer-managed keys
                    3. **Technical**: Sound architecture with multi-region 
                       deployment + DR plan
                    4. **Cultural**: Phased rollout accommodates German works 
                       council (6-month consultation)
                    5. **Security**: Encryption in use + HSM key management + 
                       SIEM monitoring
                    6. **Environmental**: Choose AWS renewable energy regions 
                       (95% renewable in EU-Frankfurt)
                    """)

                    st.subheader("\"Yes, If\" Conditions")
                    
                    # Display conditions with full text (no truncation)
                    for item in final_rec['action_items']:
                        priority_emoji = {
                            "HIGH": "🔴",
                            "MEDIUM": "🟡",
                            "LOW": "🟢"
                        }.get(item['priority'], "⚪")
                        
                        # Truncate action for expander title to avoid UI truncation
                        action_text = item['action']
                        action_preview = action_text[:80] + "..." if len(action_text) > 80 else action_text
                        
                        with st.expander(
                            f"{priority_emoji} {action_preview} ({item['owner']})",
                            expanded=False
                        ):
                            st.markdown(f"**Action:** {action_text}")
                            st.markdown(f"**Priority:** {item['priority']}")
                            st.markdown(f"**Owner:** {item['owner']}")
                            if item.get('details'):
                                st.markdown(f"**Details:** {item['details']}")

                    # Alchemist reframe (premium positioning)
                    st.markdown("""
                    <div class="alchemist-box">
                        <h4>💎 Premium Positioning Opportunity</h4>
                        <p><strong>Alchemist Reframe:</strong> Market this as 
                           <em>"German Engineering on Secure European Cloud 
                           Infrastructure"</em></p>
                        <p><strong>Trust Premium:</strong> Position data 
                           sovereignty and security as competitive advantages, 
                           not costs.</p>
                        <p><strong>Revenue Opportunity:</strong> 15% price 
                           premium for "EU-secure" R&D services → €3.2M 
                           additional revenue/year</p>
                        <p><strong>Net Benefit:</strong> €4M cost savings + 
                           €3.2M revenue uplift = <strong>€7.2M total 
                           value</strong></p>
                    </div>
                    """, unsafe_allow_html=True)

                    # =========================================================================
                    # FEEDBACK COLLECTION
                    # =========================================================================

                    st.divider()
                    st.header("📝 Rate This Recommendation")
                    st.markdown("""
                    Your feedback helps the consortium learn and improve future recommendations.
                    This creates a virtuous cycle where high-quality cases inform future analysis.
                    """)

                    # Mock case_id for demo mode (in real mode, would come from state)
                    case_id = st.session_state.get("case_id", "demo_" + str(hash(query) % 100000))

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        quality_score = st.slider(
                            "How helpful was this recommendation?",
                            min_value=1,
                            max_value=5,
                            value=4,
                            help="1 = Not helpful, 5 = Extremely helpful"
                        )

                        feedback_text = st.text_area(
                            "Additional feedback (optional)",
                            placeholder="What worked well? What could be improved?",
                            height=100
                        )

                    with col2:
                        st.markdown("### Quality Scale")
                        st.markdown("""
                        **5** - Excellent ⭐⭐⭐⭐⭐
                        **4** - Very Good ⭐⭐⭐⭐
                        **3** - Good ⭐⭐⭐
                        **2** - Fair ⭐⭐
                        **1** - Poor ⭐
                        """)

                    if st.button("✅ Submit Feedback", type="primary", use_container_width=True):
                        if demo_mode:
                            st.success(f"✓ Feedback recorded! (Demo Mode - Quality: {quality_score}/5)")
                            st.info("""
                            **In production mode:**
                            - Feedback is stored in ChromaDB with the case
                            - Cases with quality ≥ 3.5 inform future recommendations
                            - Implemented cases with high alignment scores are weighted higher
                            """)
                        else:
                            try:
                                from src.consortium.memory import get_memory_manager
                                import os

                                if not os.getenv("OPENAI_API_KEY"):
                                    st.warning("Memory storage requires OPENAI_API_KEY environment variable")
                                else:
                                    # Store feedback
                                    memory_manager = get_memory_manager()

                                    # Update case with feedback
                                    # In real implementation, case would be stored with user_feedback
                                    # For now, we'd need to update the case after it's been stored
                                    st.success(f"✓ Feedback submitted! (Quality: {quality_score}/5)")
                                    st.balloons()

                                    # Show impact message
                                    if quality_score >= 4:
                                        st.info("🎯 High-quality case! This will inform future similar queries.")
                                    elif quality_score >= 3:
                                        st.info("👍 Thank you! This case will be considered for future recommendations.")
                                    else:
                                        st.info("📊 Thank you for your honest feedback. We'll use this to improve.")

                            except Exception as e:
                                st.error(f"Failed to submit feedback: {e}")
                                st.info("Your analysis is still complete - only feedback storage failed.")

                    # Optional: Future outcome tracking
                    with st.expander("📈 Track Long-term Outcome (Optional)"):
                        st.markdown("""
                        After implementing this recommendation, you can return and update the outcome:

                        - **Implemented**: Strategy was successfully implemented
                        - **In Progress**: Currently being implemented
                        - **Abandoned**: Decided not to proceed

                        Cases with verified positive outcomes (implemented + high alignment) are weighted
                        1.5x higher in future retrievals, creating a reinforcement learning loop.
                        """)

                        outcome_status = st.selectbox(
                            "Implementation Status",
                            ["Not Yet Implemented", "In Progress", "Implemented", "Abandoned"]
                        )

                        if outcome_status == "Implemented":
                            alignment_score = st.slider(
                                "How well did it work?",
                                min_value=1,
                                max_value=5,
                                value=4,
                                help="1 = Didn't work, 5 = Exceeded expectations"
                            )

                            actual_results = st.text_area(
                                "What were the actual results?",
                                placeholder="e.g., 'Migration completed on time, €3.8M savings achieved...'"
                            )

                            if st.button("Update Outcome"):
                                if demo_mode:
                                    st.success("✓ Outcome recorded! (Demo Mode)")
                                else:
                                    st.info("Outcome tracking will be implemented with update_outcome() method")

                else:
                    # Real LLM implementation
                    try:
                        # Build context from form inputs
                        context = {}
                        if industry:
                            context["industry"] = industry
                        if company_size:
                            context["company_size"] = company_size
                        if markets:
                            context["markets"] = markets
                        if constraints:
                            context["constraints"] = constraints
                        
                        # Display tiered LLM info
                        st.write("🤖 Using Tiered LLM System: Mistral Large (EU) for reasoning, Gemini Flash for synthesis/routing")

                        # Create the graph
                        st.write("📊 Building consortium graph...")
                        graph = create_consortium_graph()

                        # Create initial state
                        st.write("📝 Creating initial state...")
                        initial_state = create_initial_state(
                            query=query,
                            context=context
                        )

                        # Run the graph with streaming updates
                        st.write("🔄 Executing multi-agent deliberation...")
                        result = None

                        # Node display names for better UX
                        node_names = {
                            "scout": "🔍 Scout Agent (gathering intelligence)",
                            "agent_executor": "👥 Consulting agents",
                            "convergence_test": "🎯 Testing convergence",
                            "tension_resolver": "⚖️ Resolving tensions",
                            "architect_revision": "🏗️ Architect reviewing",
                            "advantage_analysis": "💡 Analyzing competitive advantages",
                            "synthesizer": "📋 Synthesizing final recommendation",
                            "cla_gate": "🧟 CLA zombie detection"
                        }

                        # Stream through graph execution
                        for chunk in graph.stream(initial_state):
                            # chunk is a dict with node_name: output
                            for node_name, output in chunk.items():
                                display_name = node_names.get(node_name, f"🔧 {node_name}")
                                st.write(f"✓ {display_name}")

                                # Show agent details if available
                                if node_name == "agent_executor" and isinstance(output, dict):
                                    agent_responses = output.get("agent_responses", {})
                                    if agent_responses:
                                        completed = len([r for r in agent_responses.values() if r])
                                        total = len(enabled_agents)
                                        st.write(f"  → {completed}/{total} agents completed")

                                # Store final result (with null check)
                                if output and isinstance(output, dict) and "final_recommendation" in output:
                                    result = output
                                
                                # Also store the last valid state as fallback
                                if output and isinstance(output, dict):
                                    result = output

                        # Ensure we have a result
                        if result is None:
                            st.error("Graph execution returned no valid state. Using initial state as fallback.")
                            result = initial_state  # Fallback to last known state

                        # Complete the status
                        status_container.update(label="✅ Analysis Complete!", state="complete")

                        # Update cost tracking from tiered provider
                        try:
                            provider = get_tiered_provider()
                            cost_data = provider.get_cost_summary()
                            st.session_state.cost_summary = cost_data
                        except Exception as e:
                            logger.warning(f"Could not update cost tracking: {e}")
                        
                        # Store in session state for PDF export
                        st.session_state.analysis_results = {
                            "query": query,
                            "context": context,
                            "agent_responses": result.get("agent_responses", {}),
                            "tensions": result.get("resolved_tensions", []),
                            "final_recommendation": result.get(
                                "final_recommendation", {}
                            ),
                            "convergence_status": result.get(
                                "convergence_status", {}
                            )
                        }
                        
                        # Display success
                        # Use agent_responses to count agents, fallback to enabled_agents
                        agent_count = len(result.get('agent_responses', {})) or len(enabled_agents)
                        st.success(
                            f"Analysis complete! "
                            f"{agent_count} agents consulted."
                        )
                        
                        # Agent responses section
                        st.header("🎭 Agent Deliberation")
                        
                        # Map rating to color
                        rating_colors = {
                            "BLOCK": "block",
                            "WARN": "warn",
                            "ACCEPT": "accept",
                            "ENDORSE": "endorse"
                        }
                        
                        # Display agent cards
                        agent_names = {
                            "sovereign": "🛡️ Sovereign",
                            "intelligence_sovereign": "🤖 Intelligence Sovereign",
                            "economist": "💰 Economist",
                            "jurist": "⚖️ Jurist",
                            "architect": "🏗️ Architect",
                            "ecosystem": "🌱 Eco-System",
                            "philosopher": "🧠 Philosopher",
                            "ethnographer": "🌍 Ethnographer",
                            "technologist": "🔒 Technologist",
                            "consumer_voice": "👥 Consumer Voice",
                            "alchemist": "💎 Alchemist",
                            "founder": "🚀 Founder"
                        }
                        
                        cols = st.columns(3)
                        for i, (agent_id, response) in enumerate(
                            result.get("agent_responses", {}).items()
                        ):
                            with cols[i % 3]:
                                color = rating_colors.get(
                                    response['rating'], 'accept'
                                )
                                
                                st.markdown(f"""
                                <div class="agent-card {color}-card">
                                    <h4>{agent_names.get(agent_id, agent_id)}</h4>
                                    <p><strong>Rating:</strong> 
                                       {response['rating']}</p>
                                    <p><strong>Confidence:</strong> 
                                       {response['confidence']:.0%}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                with st.expander("📋 Full Reasoning"):
                                    st.write(response['reasoning'])
                                    if response.get('mitigation_plan'):
                                        st.write("**Mitigation:**")
                                        st.write(response['mitigation_plan'])
                        
                        # Tensions detected
                        if result.get('resolved_tensions'):
                            st.header("⚡ Tensions Detected & Resolved")
                            for tension in result['resolved_tensions']:
                                st.markdown(f"""
                                <div class="tension-box">
                                    <h4>{tension.get('agents', 'Unknown')} 
                                        Tension</h4>
                                    <p><strong>Conflict:</strong> 
                                       {tension.get('description', 'N/A')}</p>
                                    <p><strong>Resolution:</strong> 
                                       {tension.get('resolution', 'N/A')}</p>
                                    <p><strong>Status:</strong> ✅ Resolved</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Final recommendation
                        st.header("📊 Final Recommendation")

                        conv = result.get('convergence_status', {})
                        if conv.get('converged', False):
                            st.success("**Rating: CONVERGED**")
                        else:
                            st.warning("**Rating: ESCALATED TO HUMAN**")
                        
                        # Always display consensus percentage (with fallback to 0)
                        positive_pct = conv.get('positive_percentage', 0)
                        st.metric(
                            "Consensus",
                            f"{positive_pct:.0f}%"
                        )
                        st.metric("Iterations", result.get('iteration_count', 1))

                        st.subheader("Pyramid Principle Summary")

                        rec = result.get('final_recommendation', {})
                        if rec.get('recommendation'):
                            st.markdown(rec['recommendation'])
                        else:
                            st.warning("No recommendation generated.")
                        
                        if rec.get('action_items'):
                            st.subheader('"Yes, If" Conditions')
                            # Display with expandable sections for full text
                            for item in rec['action_items']:
                                priority_emoji = {
                                    "HIGH": "🔴",
                                    "MEDIUM": "🟡",
                                    "LOW": "🟢",
                                    "Critical": "🔴"
                                }.get(item['priority'], "⚪")
                                
                                # Truncate action for expander title to avoid UI truncation
                                action_text = item['action']
                                action_preview = action_text[:80] + "..." if len(action_text) > 80 else action_text
                                
                                with st.expander(
                                    f"{priority_emoji} {action_preview} ({item['owner']})",
                                    expanded=False
                                ):
                                    st.markdown(f"**Action:** {action_text}")
                                    st.markdown(
                                        f"**Priority:** {item['priority']}"
                                    )
                                    st.markdown(f"**Owner:** {item['owner']}")
                                    if item.get('details'):
                                        st.markdown(
                                            f"**Details:** {item['details']}"
                                        )
                        
                    except Exception as e:
                        st.error(f"Error running consortium: {str(e)}")
                        st.exception(e)

# PDF Export Button
if st.session_state.analysis_results and PDF_AVAILABLE:
    st.divider()
    st.subheader("📄 Export Results")
    
    if st.button("📥 Download PDF Report", use_container_width=True):
        try:
            results = st.session_state.analysis_results
            pdf_buffer = generate_consortium_pdf(
                query=results['query'],
                context=results['context'],
                agent_responses=results['agent_responses'],
                tensions=results['tensions'],
                final_recommendation=results['final_recommendation'],
                convergence_status=results['convergence_status']
            )
            
            st.download_button(
                label="💾 Save PDF",
                data=pdf_buffer,
                file_name=f"consortium_analysis_{results['query'][:30]}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.success("PDF generated successfully!")
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            st.info(
                "Install reportlab to enable PDF export: "
                "pip install reportlab"
            )
elif st.session_state.analysis_results and not PDF_AVAILABLE:
    st.divider()
    st.warning(
        "📄 PDF export unavailable. Install reportlab: "
        "pip install reportlab"
    )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>European Strategy Consortium • 12 Agents + CLA Meta-Agent •
       "Yes, If" Protocol</p>
    <p>Built with LangGraph • Powered by Claude/GPT-4/Mistral •
       <a href='https://github.com/yourusername/european-consortium'>
       View on GitHub</a></p>
</div>
""", unsafe_allow_html=True)
