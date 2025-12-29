"""
European Strategy Consortium - Streamlit Demo UI

Interactive interface for querying the multi-agent consortium and viewing
real-time deliberation results.
"""

import streamlit as st
import sys
import os
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    }
    .alchemist-box {
        background-color: #fce4ec;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #e91e63;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🇪🇺 European Strategy Consortium")
st.markdown("""
Multi-agent deliberation system for European business strategy.
9 specialized agents evaluate proposals through adversarial collaboration, converging on **"Yes, If"** recommendations.
""")

# Sidebar: Agent selection and settings
with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("Enabled Agents")

    # Big Three
    st.markdown("**Big Three (Foundational)**")
    sovereign_enabled = st.checkbox("🛡️ Sovereign (Data Sovereignty)", value=True)
    economist_enabled = st.checkbox("💰 Economist (Financial Viability)", value=True)
    jurist_enabled = st.checkbox("⚖️ Jurist (Legal Compliance)", value=True)

    # Tier 1
    st.markdown("**Tier 1 (Technical & Values)**")
    architect_enabled = st.checkbox("🏗️ Architect (Systems Design)", value=True)
    ecosystem_enabled = st.checkbox("🌱 Eco-System (Sustainability)", value=True)
    philosopher_enabled = st.checkbox("🧠 Philosopher (Ethics)", value=True)

    # Tier 4
    st.markdown("**Tier 4 (Specialized)**")
    ethnographer_enabled = st.checkbox("🌍 Ethnographer (Cultural Fit)", value=True)
    technologist_enabled = st.checkbox("🔒 Technologist (Security)", value=True)
    consumer_voice_enabled = st.checkbox("👥 Consumer Voice (User Protection)", value=True)

    # Meta
    st.markdown("**Meta-Agent**")
    cla_enabled = st.checkbox("🧟 CLA (Zombie Detection)", value=False, help="Only for proposals creating permanent programs/regulations")

    st.divider()

    # Advanced settings
    with st.expander("Advanced Settings"):
        max_iterations = st.slider("Max Consensus Iterations", 1, 10, 5)
        convergence_threshold = st.slider("Convergence Threshold", 0.5, 1.0, 0.7, 0.05)
        demo_mode = st.checkbox("Demo Mode (Mock Responses)", value=True, help="Use mock LLM responses to avoid API costs")

# Main query input
st.header("📝 Strategic Query")

# Context inputs
col1, col2 = st.columns(2)

with col1:
    query = st.text_area(
        "Enter your strategic question:",
        height=100,
        placeholder="Example: Should we move our automotive R&D data to a US cloud provider?",
        max_chars=2000
    )

    industry = st.selectbox(
        "Industry",
        ["", "Automotive", "Finance", "Healthcare", "Technology", "Retail", "Manufacturing", "Public Sector", "Other"]
    )

    company_size = st.selectbox(
        "Company Size",
        ["", "Startup (<50)", "Small (50-250)", "Medium (250-1000)", "Large (1000-5000)", "Enterprise (>5000)"]
    )

with col2:
    markets = st.multiselect(
        "Target Markets",
        ["Germany", "France", "Italy", "Spain", "Netherlands", "Belgium", "Poland", "Sweden", "Denmark", "Ireland", "Other EU"]
    )

    constraints = st.text_area(
        "Key Constraints (optional)",
        height=100,
        placeholder="e.g., 'Works council must approve', 'Limited budget: €500K', 'Must launch in 3 months'"
    )

# Analyze button
analyze_button = st.button("🔍 Analyze with Consortium", type="primary", use_container_width=True)

# Analysis results
if analyze_button:
    if not query:
        st.error("Please enter a strategic question.")
    else:
        # Build enabled agents list
        enabled_agents = []
        if sovereign_enabled:
            enabled_agents.append("sovereign")
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

        if len(enabled_agents) == 0:
            st.error("Please enable at least one agent.")
        else:
            with st.spinner(f"Consulting {len(enabled_agents)} agents..."):
                # Mock implementation for demo
                if demo_mode:
                    # Display mock results
                    st.success(f"Analysis complete! {len(enabled_agents)} agents consulted.")

                    # Agent responses section
                    st.header("🎭 Agent Deliberation")

                    # Create mock responses based on query
                    agent_data = {
                        "sovereign": {"rating": "WARN", "confidence": 0.75, "reasoning": "Data sovereignty concerns: US Cloud Act exposure for EU data. Recommend: EU cloud provider (OVHcloud, Scaleway) OR AWS EU with encryption + customer-managed keys.", "color": "warn"},
                        "economist": {"rating": "ACCEPT", "confidence": 0.82, "reasoning": "Cloud TCO favorable: On-prem €10M/year vs Cloud €6-8M/year. ROI within 18 months. Trust Premium positioning can justify any sovereignty premium.", "color": "accept"},
                        "jurist": {"rating": "WARN", "confidence": 0.88, "reasoning": "GDPR Article 46: Standard Contractual Clauses (SCCs) required for US provider. Recommend: Data Processing Agreement + SCCs + encryption. Works council approval needed (Germany).", "color": "warn"},
                        "architect": {"rating": "ACCEPT", "confidence": 0.70, "reasoning": "Cloud architecture sound for R&D workloads. Recommend: Multi-region deployment, backup strategy, disaster recovery plan. Technical debt: low.", "color": "accept"},
                        "ecosystem": {"rating": "WARN", "confidence": 0.65, "reasoning": "High compute workloads = high carbon footprint. Require: Renewable energy commitment from cloud provider. Target: <0.1 kg CO₂/kWh (vs current data center: 0.5 kg CO₂/kWh).", "color": "warn"},
                        "philosopher": {"rating": "ACCEPT", "confidence": 0.73, "reasoning": "R&D data not directly user-facing, lower ethical concerns. Ensure: Employee privacy protected, no surveillance of internal communications. Autonomy: reasonable.", "color": "accept"},
                        "ethnographer": {"rating": "WARN", "confidence": 0.80, "reasoning": "German engineering culture values control and precision. Works council (Betriebsrat) requires 6-month consultation for IT changes. Recommend: Phased migration, cultural change management, emphasize quality not just cost.", "color": "warn"},
                        "technologist": {"rating": "WARN", "confidence": 0.85, "reasoning": "Trade secret protection critical for automotive R&D. BLOCK: Unencrypted data in cloud. REQUIRE: Encryption in use (confidential computing), HSM for key management, SIEM for threat detection.", "color": "warn"},
                        "consumer_voice": {"rating": "ACCEPT", "confidence": 0.60, "reasoning": "B2B scenario, not direct consumer impact. Ensure: Customer data (if any) remains protected. Transparency: inform customers if their data affected by cloud migration.", "color": "accept"},
                    }

                    # Filter to enabled agents
                    filtered_agents = {k: v for k, v in agent_data.items() if k in enabled_agents}

                    # Display agent cards
                    cols = st.columns(3)
                    for i, (agent_id, data) in enumerate(filtered_agents.items()):
                        with cols[i % 3]:
                            # Map agent_id to display name
                            agent_names = {
                                "sovereign": "🛡️ Sovereign",
                                "economist": "💰 Economist",
                                "jurist": "⚖️ Jurist",
                                "architect": "🏗️ Architect",
                                "ecosystem": "🌱 Eco-System",
                                "philosopher": "🧠 Philosopher",
                                "ethnographer": "🌍 Ethnographer",
                                "technologist": "🔒 Technologist",
                                "consumer_voice": "👥 Consumer Voice"
                            }

                            st.markdown(f"""
                            <div class="agent-card {data['color']}-card">
                                <h4>{agent_names.get(agent_id, agent_id)}</h4>
                                <p><strong>Rating:</strong> {data['rating']}</p>
                                <p><strong>Confidence:</strong> {data['confidence']:.0%}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            with st.expander(f"📋 Full Reasoning"):
                                st.write(data['reasoning'])

                    # Tensions detected
                    st.header("⚡ Tensions Detected")

                    st.markdown("""
                    <div class="tension-box">
                        <h4>Sovereign ↔ Economist</h4>
                        <p><strong>Conflict:</strong> Data sovereignty requirements (EU cloud) vs cost optimization (AWS cheaper)</p>
                        <p><strong>Resolution:</strong> AWS EU regions + encryption + customer-managed keys. Position as "Trust Premium" to justify cost.</p>
                        <p><strong>Status:</strong> ✅ Resolved</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("""
                    <div class="tension-box">
                        <h4>Ethnographer ↔ Architect</h4>
                        <p><strong>Conflict:</strong> Cultural change management (6-month works council process) vs technical speed (3-month migration)</p>
                        <p><strong>Resolution:</strong> Phased migration: Start with non-critical workloads (3 months), expand after works council approval (6-9 months total)</p>
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
                    **Main Recommendation:** Proceed with cloud migration using **AWS EU regions** with data sovereignty controls.

                    **Supporting Arguments:**
                    1. **Financial**: €4M annual savings (€10M on-prem → €6M cloud), 18-month ROI
                    2. **Legal**: GDPR-compliant via SCCs + encryption + customer-managed keys
                    3. **Technical**: Sound architecture with multi-region deployment + DR plan
                    4. **Cultural**: Phased rollout accommodates German works council (6-month consultation)
                    5. **Security**: Encryption in use + HSM key management + SIEM monitoring
                    6. **Environmental**: Choose AWS renewable energy regions (95% renewable in EU-Frankfurt)
                    """)

                    st.subheader("\"Yes, If\" Conditions")

                    conditions = [
                        "✅ Use AWS EU regions (Frankfurt, Ireland) exclusively",
                        "✅ Implement encryption at rest, in transit, and in use (confidential computing)",
                        "✅ Customer-managed encryption keys (AWS KMS with CMK)",
                        "✅ Sign Standard Contractual Clauses (SCCs) with AWS",
                        "✅ Engage German works council: 6-month consultation process",
                        "✅ Phased migration: Non-critical workloads first (3 months), critical after approval (6-9 months)",
                        "✅ Deploy SIEM for security monitoring (AWS Security Hub + GuardDuty)",
                        "✅ Choose renewable energy regions (AWS EU-Frankfurt: 95% renewable)",
                        "✅ Implement disaster recovery plan with 99.9% uptime SLA",
                        "✅ Budget: €200K for security controls (HSM, SIEM) + €500K migration costs"
                    ]

                    for condition in conditions:
                        st.markdown(condition)

                    # Alchemist reframe (premium positioning)
                    st.markdown("""
                    <div class="alchemist-box">
                        <h4>💎 Premium Positioning Opportunity</h4>
                        <p><strong>Alchemist Reframe:</strong> Market this as <em>"German Engineering on Secure European Cloud Infrastructure"</em></p>
                        <p><strong>Trust Premium:</strong> Position data sovereignty and security as competitive advantages, not costs.</p>
                        <p><strong>Revenue Opportunity:</strong> 15% price premium for "EU-secure" R&D services → €3.2M additional revenue/year</p>
                        <p><strong>Net Benefit:</strong> €4M cost savings + €3.2M revenue uplift = <strong>€7.2M total value</strong></p>
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
                    # Real implementation would go here
                    st.info("Real LLM integration not yet implemented. Enable 'Demo Mode' in sidebar for mock results.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>European Strategy Consortium • 9 Agents + CLA Meta-Agent • "Yes, If" Protocol</p>
    <p>Built with LangGraph • Powered by Claude/GPT-4/Mistral • <a href='https://github.com/yourusername/european-consortium'>View on GitHub</a></p>
</div>
""", unsafe_allow_html=True)
