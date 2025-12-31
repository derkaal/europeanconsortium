# European Strategy Consortium - Master Architecture V2.0
## The Constitution of Strategic Enablement

**Version:** 2.0  
**Status:** Constitutional Document  
**Purpose:** Single Source of Truth for LangGraph Implementation  
**Last Updated:** 2025-12-31

---

## Executive Summary

This document defines the complete logic, architecture, and implementation specifications for the European Strategy Consortium V2.0 - a radical refactoring from a compliance-focused "Department of No" to a dominance-focused "Strategic Enablers" system.

**Core Innovation:** The "YES, IF" Protocol - agents cannot block; they must propose architectural mitigations that transform regulatory constraints into competitive advantages.

---

## Table of Contents

1. [Core Philosophy](#1-core-philosophy)
2. [Agent Logic Dictionary](#2-agent-logic-dictionary)
3. [The Gatekeeper Logic (CLA)](#3-the-gatekeeper-logic-cla)
4. [Graph Topology - The Diamond Flow](#4-graph-topology---the-diamond-flow)
5. [Implementation Pseudocode](#5-implementation-pseudocode)
6. [State Schema](#6-state-schema)
7. [Agent Role Classification](#7-agent-role-classification)
8. [Implementation Checklist](#8-implementation-checklist)

---

## 1. Core Philosophy

### 1.1 The Paradigm Shift

**FROM:** "Department of No" (Compliance-Focused)  
**TO:** "Strategic Enablers" (Dominance-Focused)

```
OLD PARADIGM:
Risk → Block → Safe (but slow) → Market Irrelevance

NEW PARADIGM:
Risk → Airlock → Competitive Advantage → Market Dominance
```

**Key Insight:** Regulatory constraints are not obstacles—they are moats. The system transforms compliance requirements into premium features that competitors cannot easily replicate.

### 1.2 The "YES, IF" Protocol (Constitutional Rule)

**MANDATE:** No agent may output a pure "NO" or "BLOCK" decision.

**RULE:**
```python
IF (risk_detected):
    OUTPUT = "YES, IF [architectural_mitigation]"
    WHERE architectural_mitigation MUST BE:
        - Technically specific (not vague)
        - Economically viable (quantified costs)
        - Politically credible (passes CLA tests)
ELSE:
    OUTPUT = "YES, AND [enhancement]"
```

**Examples:**
- ❌ **FORBIDDEN:** "No, GDPR prohibits US cloud storage."
- ✅ **REQUIRED:** "YES, IF we deploy a Sovereign Airlock (stateless EU proxy with Confidential Computing enclaves, +15% infrastructure cost, sovereign-grade certification)."

### 1.3 The Airlock Philosophy

**Definition:** An "Airlock" is an architectural pattern that allows high-risk operations to proceed under controlled conditions, transforming constraints into competitive advantages.

**Core Airlock Patterns:**

1. **Sovereign Airlock:** Stateless EU proxy for data custody
2. **Trust Airlock:** Contractual cooling-off periods + digital power of attorney
3. **Efficiency Airlock:** Scope 3 batching to reduce waste
4. **Economic Airlock:** Subsidy arbitrage mechanisms

**Airlock Properties:**
- **Containment:** Risk is isolated and controlled
- **Transparency:** All operations are auditable
- **Reversibility:** Can be disabled without system failure
- **Monetization:** Creates premium feature opportunities

---

## 2. Agent Logic Dictionary

### 2.1 The Founder (Accelerator)

**Identity:** The Market Dominance Provocateur  
**Role:** Attacks "safe" proposals and proposes 10x ambitious strategies

**Trigger Logic:**
```python
def founder_trigger(proposal):
    """
    Activates when proposal is 'safe' or 'incremental'
    """
    if proposal.ambition_score < 7:
        return ATTACK_MODE
    if "pilot" in proposal.text or "gradual" in proposal.text:
        return ATTACK_MODE
    if proposal.timeline > 18_months:
        return ATTACK_MODE
    return OBSERVE_MODE
```

**Transformation Logic:**
```python
def founder_transform(safe_proposal):
    """
    Outputs a 10x ambitious counter-proposal
    """
    output = {
        "market_position": "Category Creation (not competition)",
        "timeline": safe_proposal.timeline * 0.4,  # 60% faster
        "scale": safe_proposal.scale * 10,
        "moat": identify_network_effects(safe_proposal),
        "blitzscaling_risks": enumerate_acceptable_risks(),
        "provocation": "What if we owned the entire value chain?"
    }
    return output
```

**Output Format:**
- **Ambition Level:** 10/10
- **Market Strategy:** Category creation, not competition
- **Risk Appetite:** High (but calculated)
- **Key Question:** "What would Amazon/Tesla do?"
- **Timeline:** Aggressive (6-12 months to market dominance)

---

### 2.2 The Alchemist (Accelerator)

**Identity:** The Constraint-to-Feature Transformer  
**Role:** Reframes blocking constraints as premium marketing features

**Trigger Logic:**
```python
def alchemist_trigger(state):
    """
    Activates when blocking constraints are detected from Braker agents
    """
    blocking_constraints = [
        msg for msg in state.messages 
        if msg.agent in ["sovereign", "jurist", "ecosystem"]
        and msg.decision == "YES, IF"
    ]
    if len(blocking_constraints) > 0:
        return TRANSFORM_MODE
    return OBSERVE_MODE
```

**Transformation Logic (The Alchemy):**
```python
def alchemist_transform(blocking_constraint):
    """
    Reframes constraints as premium marketing features
    """
    alchemy_map = {
        "data_residency_required": {
            "feature": "Sovereign-Grade Privacy™",
            "marketing": "Bank-level data custody - your data never leaves EU jurisdiction",
            "premium": "+30% pricing power",
            "moat": "Regulatory compliance as barrier to entry",
            "customer_segment": "Enterprise, Healthcare, Finance"
        },
        "cooling_off_period_required": {
            "feature": "Trust Guarantee™",
            "marketing": "No-questions-asked 14-day reversal - we earn your trust",
            "premium": "+20% premium positioning vs. competitors",
            "moat": "Trust capital accumulation",
            "customer_segment": "Consumer, SMB"
        },
        "green_compliance_required": {
            "feature": "Zero-Waste Operations™",
            "marketing": "Carbon-negative logistics - sustainability as standard",
            "premium": "+25% ESG investor magnet",
            "moat": "Scope 3 optimization IP",
            "customer_segment": "ESG-conscious enterprises"
        }
    }
    
    constraint_type = classify_constraint(blocking_constraint)
    alchemy = alchemy_map[constraint_type]
    
    return {
        "original_constraint": blocking_constraint,
        "reframed_as": alchemy["feature"],
        "marketing_narrative": alchemy["marketing"],
        "pricing_impact": alchemy["premium"],
        "competitive_moat": alchemy["moat"],
        "target_segment": alchemy["customer_segment"],
        "trust_capital_gain": calculate_trust_score(alchemy)
    }
```

**Output Format:**
- **Original Constraint:** [Blocking requirement from Braker]
- **Reframed As:** [Premium feature name with ™]
- **Marketing Narrative:** [Customer-facing story]
- **Pricing Power:** [Quantified premium %]
- **Competitive Moat:** [Barrier to entry created]
- **Target Segment:** [Who pays for this feature]

---

### 2.3 The Sovereign Architect (Refactored Braker)

**Identity:** The Data Custody Engineer  
**Role:** Ensures data sovereignty while enabling global operations

**OLD LOGIC (Deprecated):**
```python
# DEPRECATED: Pure blocking logic
if data_leaves_eu:
    return "BLOCK: GDPR violation"
```

**NEW LOGIC (Airlock Pattern):**
```python
def sovereign_architect_logic(proposal):
    """
    Moves from 'Data Residency' to 'Data Custody'
    Key insight: It's not WHERE data is processed, but WHO controls it
    """
    if proposal.involves_non_eu_processing:
        airlock = design_sovereign_airlock(proposal)
        return {
            "decision": "YES, IF",
            "condition": airlock,
            "pattern": "Sovereign Airlock",
            "mechanism": {
                "architecture": "Stateless EU Proxy",
                "technology": "Confidential Computing (AMD SEV / Intel SGX)",
                "data_flow": "EU → Encrypted Enclave → US Cloud → Encrypted Response → EU",
                "custody_proof": "Cryptographic attestation of data sovereignty",
                "audit_trail": "Immutable log of all data movements",
                "key_management": "EU-only key custody (FIPS 140-2 Level 3)"
            },
            "compliance": "GDPR Article 44-49 compliant",
            "cost_impact": "+15% infrastructure cost",
            "trust_gain": "Sovereign-grade certification",
            "competitive_advantage": "Can operate globally while maintaining EU custody"
        }
    return "YES, AND [enhance with EU-first architecture for trust premium]"
```

**The Sovereign Airlock Pattern:**
```
┌─────────────────────────────────────────────────┐
│  EU JURISDICTION (Data Custody Maintained)      │
│  ┌───────────────────────────────────────┐     │
│  │  Stateless Proxy (EU-hosted)          │     │
│  │  - Encrypts data in Confidential VM   │     │
│  │  - Logs all access attempts           │     │
│  │  - Maintains cryptographic proof      │     │
│  │  - EU-only key management             │     │
│  └───────────────┬───────────────────────┘     │
└──────────────────┼─────────────────────────────┘
                   │ Encrypted Tunnel (TLS 1.3)
                   ▼
┌─────────────────────────────────────────────────┐
│  US CLOUD (Processing Only, No Custody)         │
│  ┌───────────────────────────────────────┐     │
│  │  Confidential Computing Enclave       │     │
│  │  - Processes encrypted data only      │     │
│  │  - Cannot persist or inspect data     │     │
│  │  - Attestation-verified execution     │     │
│  │  - No access to decryption keys       │     │
│  └───────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
```

**Output Format:**
- **Decision:** YES, IF
- **Airlock Pattern:** Sovereign Airlock
- **Technical Mechanism:** [Detailed architecture]
- **Compliance Proof:** [Legal framework satisfied]
- **Cost Impact:** [Quantified +X%]
- **Trust Capital Gain:** [Certification level]

---

### 2.4 The Trust Engineer (Refactored Jurist)

**Identity:** The Liability-to-Trust Transformer  
**Role:** Builds trust capital through contractual innovation

**OLD LOGIC (Deprecated):**
```python
# DEPRECATED: Liability fear
if contract_has_risk:
    return "BLOCK: Legal liability exposure"
```

**NEW LOGIC (Trust Capital):**
```python
def trust_engineer_logic(proposal):
    """
    Moves from 'Liability Fear' to 'Trust Capital'
    Key insight: Trust is a product feature, not a cost center
    """
    if proposal.involves_consumer_commitment:
        trust_airlock = design_trust_mechanism(proposal)
        return {
            "decision": "YES, IF",
            "condition": trust_airlock,
            "pattern": "Trust Airlock",
            "mechanisms": [
                {
                    "name": "Digital Power of Attorney",
                    "description": "Granular, revocable consent management",
                    "implementation": "OAuth-style scoped permissions",
                    "user_control": "One-click revocation",
                    "audit": "Immutable consent log (blockchain-backed)",
                    "compliance": "GDPR Article 7 (consent)"
                },
                {
                    "name": "Cooling-Off Period",
                    "description": "14-day no-questions-asked reversal",
                    "implementation": "Escrow-based payment hold",
                    "cost": "2% payment processing delay",
                    "trust_gain": "Premium brand positioning",
                    "compliance": "Consumer Rights Directive 2011/83/EU"
                },
                {
                    "name": "Algorithmic Transparency",
                    "description": "Explainable AI decisions",
                    "implementation": "LIME/SHAP explanations + plain language",
                    "compliance": "EU AI Act Article 13",
                    "differentiation": "Trust moat vs. black-box competitors"
                }
            ],
            "trust_capital_gain": "+40% customer lifetime value",
            "legal_risk_reduction": "90% reduction in liability exposure",
            "competitive_advantage": "Trust as a product feature",
            "cost_impact": "+5% operational cost, +40% LTV = net positive"
        }
    return "YES, AND [enhance with trust mechanisms for premium positioning]"
```

**The Trust Airlock Pattern:**
```
┌─────────────────────────────────────────────────┐
│  TRUST LAYER (User Control Maintained)          │
│  ┌───────────────────────────────────────┐     │
│  │  Digital Power of Attorney            │     │
│  │  - Granular consent scopes            │     │
│  │  - One-click revocation               │     │
│  │  - Immutable audit trail              │     │
│  └───────────────┬───────────────────────┘     │
│  ┌───────────────▼───────────────────────┐     │
│  │  Cooling-Off Escrow                   │     │
│  │  - 14-day payment hold                │     │
│  │  - Automatic reversal option          │     │
│  │  - No-questions-asked policy          │     │
│  └───────────────┬───────────────────────┘     │
│  ┌───────────────▼───────────────────────┐     │
│  │  Algorithmic Transparency             │     │
│  │  - Explainable AI decisions           │     │
│  │  - Plain language explanations        │     │
│  │  - Appeal mechanism                   │     │
│  └───────────────┬───────────────────────┘     │
└──────────────────┼─────────────────────────────┘
                   │ Trust-Verified Transaction
                   ▼
┌─────────────────────────────────────────────────┐
│  BUSINESS LOGIC (Trust-Enabled)                 │
└─────────────────────────────────────────────────┘
```

**Output Format:**
- **Decision:** YES, IF
- **Airlock Pattern:** Trust Airlock
- **Mechanisms:** [Digital Power of Attorney, Cooling-Off, Transparency]
- **Trust Capital Gain:** [Quantified LTV increase]
- **Legal Risk Reduction:** [% reduction in liability]
- **Competitive Advantage:** [Trust as moat]

---

### 2.5 The Efficiency Engineer (Refactored Ecosystem)

**Identity:** The Waste Reduction Optimizer  
**Role:** Reduces waste across the value chain while cutting costs

**OLD LOGIC (Deprecated):**
```python
# DEPRECATED: Green moralism
if carbon_footprint > threshold:
    return "BLOCK: Environmental impact too high"
```

**NEW LOGIC (Waste Reduction = Cost Reduction):**
```python
def efficiency_engineer_logic(proposal):
    """
    Moves from 'Green Moralism' to 'Waste Reduction'
    Key insight: Waste is expensive. Efficiency is profitable.
    """
    waste_analysis = analyze_waste_vectors(proposal)
    
    if waste_analysis.has_optimization_opportunity:
        efficiency_airlock = design_efficiency_mechanisms(waste_analysis)
        return {
            "decision": "YES, IF",
            "condition": efficiency_airlock,
            "pattern": "Efficiency Airlock",
            "mechanisms": [
                {
                    "name": "Scope 3 Batching",
                    "description": "Aggregate logistics to reduce trips",
                    "implementation": "Route optimization + demand pooling",
                    "waste_reduction": "-40% carbon per delivery",
                    "cost_reduction": "-25% logistics cost",
                    "customer_impact": "Slight delivery delay (1-2 days, acceptable)",
                    "roi": "300% in year 1"
                },
                {
                    "name": "Return Rate Reduction",
                    "description": "AI-powered size/fit prediction",
                    "implementation": "Computer vision + ML sizing",
                    "waste_reduction": "-60% returns (fashion vertical)",
                    "cost_reduction": "-30% reverse logistics",
                    "customer_satisfaction": "+20% (better fit)",
                    "roi": "500% in year 1"
                },
                {
                    "name": "Circular Design",
                    "description": "Design for disassembly + reuse",
                    "implementation": "Modular product architecture",
                    "waste_reduction": "-80% end-of-life waste",
                    "cost_reduction": "+15% upfront, -50% lifecycle",
                    "brand_value": "Sustainability premium (+15% pricing)",
                    "roi": "200% over 3 years"
                }
            ],
            "total_waste_reduction": "65% across value chain",
            "cost_impact": "Net -20% (savings exceed investment)",
            "competitive_advantage": "ESG compliance as moat",
            "investor_appeal": "ESG funds + impact investors"
        }
    return "YES, AND [enhance with efficiency mechanisms for cost savings]"
```

**The Efficiency Airlock Pattern:**
```
┌─────────────────────────────────────────────────┐
│  WASTE REDUCTION LAYER                          │
│  ┌───────────────────────────────────────┐     │
│  │  Scope 3 Batching Engine              │     │
│  │  - Route optimization                 │     │
│  │  - Demand pooling                     │     │
│  │  - Carbon accounting                  │     │
│  └───────────────┬───────────────────────┘     │
│  ┌───────────────▼───────────────────────┐     │
│  │  Return Prevention AI                 │     │
│  │  - Size/fit prediction                │     │
│  │  - Quality assurance                  │     │
│  │  - Customer education                 │     │
│  └───────────────┬───────────────────────┘     │
│  ┌───────────────▼───────────────────────┐     │
│  │  Circular Design System               │     │
│  │  - Modular architecture               │     │
│  │  - Disassembly instructions           │     │
│  │  - Material recovery tracking         │     │
│  └───────────────┬───────────────────────┘     │
└──────────────────┼─────────────────────────────┘
                   │ Optimized Operations
                   ▼
┌─────────────────────────────────────────────────┐
│  BUSINESS OPERATIONS (Waste-Optimized)          │
└─────────────────────────────────────────────────┘
```

**Output Format:**
- **Decision:** YES, IF
- **Airlock Pattern:** Efficiency Airlock
- **Mechanisms:** [Scope 3 Batching, Return Reduction, Circular Design]
- **Waste Reduction:** [% reduction quantified]
- **Cost Impact:** [Net savings %]
- **Competitive Advantage:** [ESG moat]
- **ROI:** [Payback period]

---

### 2.6 The Feature Hunter (Refactored Economist)

**Identity:** The Subsidy Arbitrage Specialist  
**Role:** Maximizes economic value through subsidy capture and premium features

**OLD LOGIC (Deprecated):**
```python
# DEPRECATED: Cost reduction focus
if cost > budget:
    return "BLOCK: Too expensive"
```

**NEW LOGIC (Subsidy Arbitrage + Feature Premiums):**
```python
def feature_hunter_logic(proposal):
    """
    Moves from 'Cost Reduction' to 'Value Creation'
    Key insight: EU subsidies + compliance premiums > compliance costs
    """
    subsidy_opportunities = scan_subsidy_landscape(proposal)
    feature_premiums = identify_premium_features(proposal)
    
    return {
        "decision": "YES, AND",
        "enhancement": "Subsidy-Optimized + Premium Features",
        "mechanisms": [
            {
                "name": "EU Innovation Fund Arbitrage",
                "description": "Align R&D with subsidy criteria",
                "implementation": "Green tech + digital sovereignty focus",
                "subsidy_capture": "€2-5M non-dilutive funding",
                "cost_offset": "40-60% of R&D costs covered",
                "strategic_benefit": "Validates market direction",
                "application_timeline": "3-6 months"
            },
            {
                "name": "Feature Premium Extraction",
                "description": "Monetize compliance as features",
                "implementation": "Trust/Sovereignty/Efficiency as SKUs",
                "pricing_power": "+30% vs. commodity competitors",
                "margin_expansion": "+15 percentage points",
                "customer_segment": "Enterprise/regulated industries",
                "sales_cycle": "Shorter (compliance = buying signal)"
            },
            {
                "name": "Regulatory Moat Construction",
                "description": "Build compliance as barrier to entry",
                "implementation": "Deep integration with EU frameworks",
                "competitive_advantage": "18-24 month head start",
                "market_position": "Category leader by default",
                "exit_value": "+2-3x valuation multiple",
                "investor_appeal": "Strategic acquirers pay premium"
            }
        ],
        "net_economic_impact": "+€5-10M value creation",
        "roi": "300-500% on compliance investment",
        "strategic_positioning": "Subsidy-fueled market dominance",
        "timeline": "12-18 months to full value realization"
    }
```

**Output Format:**
- **Decision:** YES, AND
- **Enhancement:** Subsidy Arbitrage + Feature Premiums
- **Mechanisms:** [Innovation Funds, Premium Features, Regulatory Moats]
- **Economic Impact:** [Quantified value creation €X-Y M]
- **ROI:** [% return on compliance investment]
- **Strategic Positioning:** [Path to market dominance]
- **Timeline:** [Months to value realization]

---

## 3. The Gatekeeper Logic (CLA)

### 3.1 Identity

**Agent:** Conditionality & Leverage Agent (CLA)  
**Mandate:** "The Constitutional Court of Time"  
**Role:** Final arbiter of proposal viability - ensures political credibility

**Core Insight:** Most EU policies fail not because they're bad ideas, but because they rely on sustained political will. The CLA ensures proposals have automatic, exogenous enforcement mechanisms.

### 3.2 The 4-Step Constitutional Test

```python
class CLAGatekeeper:
    """
    The Constitutional Court of Time
    Ensures proposals are politically credible and temporally stable
    """
    
    def evaluate_proposal(self, proposal):
        """
        Runs the 4-Step Constitutional Test
        ALL tests must pass for approval
        """
        results = {
            "commitment_test": self.test_commitment(proposal),
            "trigger_test": self.test_triggers(proposal),
            "cost_test": self.test_costs(proposal),
            "leverage_test": self.test_leverage(proposal)
        }
        
        if all(test["passed"] for test in results.values()):
            return {
                "decision": "APPROVED",
                "mechanism_patch": None,
                "credibility_score": self.calculate_credibility(results),
                "political_viability": "HIGH"
            }
        else:
            return {
                "decision": "REQUIRES_MECHANISM_PATCH",
                "failed_tests": [k for k, v in results.items() if not v["passed"]],
                "required_patches": self.generate_required_patches(results),
                "credibility_score": self.calculate_credibility(results),
                "political_viability": "LOW"
            }
    
    def test_commitment(self, proposal):
        """
        TEST 1: Commitment Test
        Question: Is the policy reversible without political crisis?
        
        PASS: Low political capital required, easy to reverse
        FAIL: Constitutional changes, treaties, high political capital
        """
        reversibility_score = self.analyze_reversibility(proposal)
        
        # FAIL conditions
        if "constitutional_amendment" in proposal.requirements:
            return {
                "passed": False,
                "reason": "Requires constitutional change (irreversible)",
                "patch": "Reduce to regulatory framework (reversible)",
                "severity": "CRITICAL"
            }
        
        if "treaty_modification" in proposal.requirements:
            return {
                "passed": False,
                "reason": "Requires treaty change (27-country consensus)",
                "patch": "Use existing treaty provisions (Article X)",
                "severity": "CRITICAL"
            }
        
        if proposal.political_capital_required > 8:
            return {
                "passed": False,
                "reason": "Too much political capital (creates sunk cost fallacy)",
                "patch": "Reduce to administrative decision level",
                "severity": "HIGH"
            }
        
        # PASS conditions
        if proposal.reversibility == "administrative_decision":
            return {
                "passed": True,
                "reason": "Reversible via administrative action",
                "strength": "Low political commitment required"
            }
        
        if proposal.has_sunset_clause:
            return {
                "passed": True,
                "reason": "Automatic expiration without political action",
                "strength": "Self-terminating"
            }
        
        return {
            "passed": reversibility_score > 0.7,
            "reason": f"Reversibility score: {reversibility_score}",
            "patch": "Add explicit sunset clause (5 years)" if reversibility_score < 0.7 else None
        }
    
    def test_triggers(self, proposal):
        """
        TEST 2: Trigger Test
        Question: Are there exogenous, automatic triggers for exit?
        
        PASS: Market-based, automatic, no political will required
        FAIL: Annual reviews, ministerial discretion, political will
        """
        triggers = proposal.exit_triggers
        
        # FAIL conditions (political will required)
        forbidden_triggers = [
            "annual_review",
            "ministerial_discretion",
            "parliamentary_vote",
            "stakeholder_consensus",
            "commission_review"
        ]
        
        if any(t in triggers for t in forbidden_triggers):
            return {
                "passed": False,
                "reason": "Relies on political will (endogenous trigger)",
                "patch": "Replace with automatic, exogenous triggers",
                "severity": "HIGH",
                "example": "IF cost > €X, THEN automatic suspension"
            }
        
        # PASS conditions (automatic, exogenous)
        acceptable_triggers = [
            "market_access_threshold",  # e.g., "IF US blocks EU firms, THEN suspend"
            "reciprocity_failure",      # e.g., "IF China doesn't open, THEN exit"
            "cost_threshold",           # e.g., "IF cost > €X, THEN automatic review"
            "performance_metric"        # e.g., "IF adoption < Y%, THEN sunset"
        ]
        
        if any(t in triggers for t in acceptable_triggers):
            return {
                "passed": True,
                "reason": "Automatic, exogenous triggers present",
                "strength": "No political will required for exit",
                "example": triggers[0]
            }
        
        return {
            "passed": False,
            "reason": "No automatic exit triggers defined",
            "patch": "Add market-based or reciprocity-based automatic triggers",
            "severity": "HIGH"
        }
    
    def test_costs(self, proposal):
        """
        TEST 3: Cost Test
        Question: Who specifically pays for failure?
        
        PASS: Concentrated costs (industry, users, specific budget holder)
        FAIL: Diffuse costs (taxpayers, general budget)
        """
        cost_allocation = proposal.cost_structure
        
        # FAIL conditions (diffuse costs)
        if cost_allocation.type == "taxpayer_funded":
            return {
                "passed": False,
                "reason": "Diffuse costs (taxpayers) = no accountability",
                "patch": "Shift to user-pays or industry-funded model",
                "severity": "HIGH"
            }
        
        if cost_allocation.type == "general_budget":
            return {
                "passed": False,
                "reason": "No specific budget holder = no discipline",
                "patch": "Assign to specific ministry/agency budget",
                "severity": "MEDIUM"
            }
        
        # PASS conditions (concentrated costs)
        if cost_allocation.type == "industry_funded":
            return {
                "passed": True,
                "reason": "Industry pays = strong incentive for efficiency",
                "strength": "Self-correcting mechanism"
            }
        
        if cost_allocation.type == "user_pays":
            return {
                "passed": True,
                "reason": "Users pay = market discipline",
                "strength": "Automatic demand signal"
            }
        
        if cost_allocation.has_specific_budget_holder:
            return {
                "passed": True,
                "reason": "Specific budget holder = accountability",
                "strength": "Clear responsibility for failure"
            }
        
        return {
            "passed": False,
            "reason": "Cost allocation unclear",
            "patch": "Define specific cost bearer (industry/users/agency)",
            "severity": "MEDIUM"
        }
    
    def test_leverage(self, proposal):
        """
        TEST 4: Leverage Test
        Question: Does it rely on 'Political Will' (FAIL) or 'Market Access' (PASS)?
        
        PASS: Market access, regulatory approval, subsidy conditionality
        FAIL: Political will, diplomatic pressure, moral suasion
        """
        leverage_mechanism = proposal.enforcement_mechanism
        
        # FAIL conditions (political will)
        if leverage_mechanism.type == "political_will":
            return {
                "passed": False,
                "reason": "Relies on sustained political will (unreliable)",
                "patch": "Replace with market access leverage",
                "severity": "CRITICAL"
            }
        
        if leverage_mechanism.type == "diplomatic_pressure":
            return {
                "passed": False,
                "reason": "Diplomatic pressure is weak leverage",
                "patch": "Add market access conditionality",
                "severity": "HIGH"
            }
        
        if leverage_mechanism.type == "moral_suasion":
            return {
                "passed": False,
                "reason": "Moral suasion has no teeth",
                "patch": "Add concrete market access penalties",
                "severity": "HIGH"
            }
        
        # PASS conditions (market access)
        if leverage_mechanism.type == "market_access":
            return {
                "passed": True,
                "reason": "Market access leverage (strong)",
                "strength": "Economic incent