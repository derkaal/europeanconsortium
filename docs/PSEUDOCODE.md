# PSEUDOCODE - Phase P

**Project**: European Strategy Consortium Multi-Agent System  
**Methodology**: SPARC Phase P (Pseudocode)  
**Date**: 2024-12-24  
**Status**: DRAFT - Awaiting Approval

---

## Overview

This document contains algorithmic logic in structured English for the five core systems of the European Strategy Consortium. This is NOT implementation code - it defines the logic that will be implemented in Phase A (Architecture) and Phase R (Refinement).

**Sections**:
1. Supervisor Routing Algorithm
2. All Five Tension Protocols
3. Convergence Testing Algorithm
4. Memory Retrieval Strategy
5. Knowledge Access Routing Logic

---

## 1. SUPERVISOR ROUTING ALGORITHM

### 1.1 Main Routing Function

```
FUNCTION route_query_to_agents(query, conversation_state):
    // Analyzes query and determines which agents should be engaged
    // Returns list of agent IDs and sub-questions assigned to each
    
    // Extract keywords and analyze query complexity
    keywords = extract_keywords(query)
    query_embedding = generate_query_embedding(query)
    complexity_score = assess_query_complexity(query, conversation_state)
    
    // Initialize agent engagement tracker
    triggered_agents = []
    agent_confidence_scores = {}
    
    // ALWAYS engage core agents
    triggered_agents.ADD("Economist")  // Financial viability always required
    triggered_agents.ADD("Architect")   // Technical feasibility always required
    agent_confidence_scores["Economist"] = 1.0
    agent_confidence_scores["Architect"] = 1.0
    
    // Stage 1: Keyword-based domain mapping
    keyword_matches = map_keywords_to_domains(keywords)
    FOR EACH domain IN keyword_matches:
        agent_id = get_agent_for_domain(domain)
        IF agent_id NOT IN triggered_agents THEN
            triggered_agents.ADD(agent_id)
            agent_confidence_scores[agent_id] = keyword_matches[domain].confidence
        END IF
    END FOR
    
    // Stage 2: Semantic similarity to agent mandates
    FOR EACH agent IN all_available_agents:
        IF agent NOT IN triggered_agents THEN
            // agent_embedding is pre-computed from agent.mandate_text on system startup
            // Cached in memory for performance (1536-dim vector from text-embedding-3-small)
            mandate_embedding = get_agent_mandate_embedding(agent)
            similarity = cosine_similarity(query_embedding, mandate_embedding)
            
            IF similarity > 0.6 THEN  // Confidence threshold
                triggered_agents.ADD(agent)
                agent_confidence_scores[agent] = similarity
            END IF
        END IF
    END FOR
    
    // Stage 3: LLM-based classification for ambiguous cases
    IF complexity_score > 0.7 THEN  // Complex query needs validation
        llm_analysis = invoke_llm_for_agent_classification(query, triggered_agents)
        
        FOR EACH suggested_agent IN llm_analysis.agents:
            IF suggested_agent NOT IN triggered_agents AND llm_analysis.confidence[suggested_agent] > 0.6 THEN
                triggered_agents.ADD(suggested_agent)
                agent_confidence_scores[suggested_agent] = llm_analysis.confidence[suggested_agent]
            END IF
        END FOR
    END IF
    
    // Complexity overload check
    IF COUNT(triggered_agents) > 7 THEN
        // Rank by confidence and keep top 7
        ranked_agents = sort_by_confidence(triggered_agents, agent_confidence_scores)
        triggered_agents = ranked_agents[0:7]
        
        LOG_WARNING("Complexity overload: reduced from " + COUNT(all_matched) + " to 7 agents")
    END IF
    
    // Decompose query into sub-questions
    sub_questions = decompose_query(query, triggered_agents)
    
    // Validate MECE property
    mece_validation = validate_mece(sub_questions)
    IF NOT mece_validation.is_valid THEN
        // Revise sub-questions to ensure MECE
        sub_questions = revise_for_mece(sub_questions, mece_validation.gaps, mece_validation.overlaps)
    END IF
    
    // Assign sub-questions to agents
    assignments = assign_subquestions_to_agents(sub_questions, triggered_agents, agent_confidence_scores)
    
    // Update state graph
    UPDATE_STATE(conversation_state, {
        "triggered_agents": triggered_agents,
        "agent_confidence_scores": agent_confidence_scores,
        "sub_questions": sub_questions,
        "assignments": assignments,
        "routing_timestamp": current_timestamp()
    })
    
    RETURN {
        "agents": triggered_agents,
        "assignments": assignments,
        "initial_confidence": agent_confidence_scores
    }
END FUNCTION
```

### 1.2 Keyword Extraction and Domain Mapping

```
FUNCTION map_keywords_to_domains(keywords):
    // Maps extracted keywords to agent knowledge domains
    // Returns dictionary of {domain: {agent: str, confidence: float}}
    
    domain_map = {}
    
    // Define keyword → domain mappings
    sovereignty_keywords = ["vendor lock-in", "data residency", "CLOUD Act", "Gaia-X", "sovereignty", "EU-only", "external key management", "TEE"]
    legal_keywords = ["GDPR", "AI Act", "DSA", "compliance", "regulation", "liability", "contract", "terms of service"]
    environmental_keywords = ["carbon", "SCI", "emissions", "sustainability", "energy", "planetary boundaries", "green"]
    economic_keywords = ["cost", "ROI", "budget", "TCO", "unit economics", "CAPEX", "OPEX", "financial"]
    architectural_keywords = ["microservices", "architecture", "infrastructure", "scalability", "system design", "IaC"]
    ethical_keywords = ["bias", "fairness", "transparency", "dark patterns", "Constitutional AI", "values"]
    cultural_keywords = ["organizational", "culture", "change management", "Hofstede", "resistance"]
    security_keywords = ["vulnerability", "encryption", "HSM", "incident response", "penetration testing", "SIEM"]
    consumer_keywords = ["user rights", "accessibility", "WCAG", "consumer protection", "BEUC"]
    future_keywords = ["scenario", "disruption", "quantum", "geopolitical", "long-term", "technology evolution"]
    operational_keywords = ["implementation", "timeline", "resources", "capacity", "procurement", "project management"]
    
    FOR EACH keyword IN keywords:
        IF keyword IN sovereignty_keywords THEN
            domain_map["sovereignty"] = {"agent": "Sovereign", "confidence": 0.9}
        ELSE IF keyword IN legal_keywords THEN
            domain_map["legal"] = {"agent": "Jurist", "confidence": 0.9}
        ELSE IF keyword IN environmental_keywords THEN
            domain_map["environmental"] = {"agent": "Eco-System", "confidence": 0.9}
        ELSE IF keyword IN economic_keywords THEN
            domain_map["economic"] = {"agent": "Economist", "confidence": 0.9}
        ELSE IF keyword IN architectural_keywords THEN
            domain_map["technical"] = {"agent": "Architect", "confidence": 0.9}
        ELSE IF keyword IN ethical_keywords THEN
            domain_map["ethical"] = {"agent": "Philosopher", "confidence": 0.9}
        ELSE IF keyword IN cultural_keywords THEN
            domain_map["cultural"] = {"agent": "Ethnographer", "confidence": 0.9}
        ELSE IF keyword IN security_keywords THEN
            domain_map["security"] = {"agent": "Technologist", "confidence": 0.9}
        ELSE IF keyword IN consumer_keywords THEN
            domain_map["consumer"] = {"agent": "Consumer Voice", "confidence": 0.9}
        ELSE IF keyword IN future_keywords THEN
            domain_map["foresight"] = {"agent": "Futurist", "confidence": 0.9}
        ELSE IF keyword IN operational_keywords THEN
            domain_map["operational"] = {"agent": "Operator", "confidence": 0.9}
        END IF
    END FOR
    
    RETURN domain_map
END FUNCTION
```

### 1.3 Query Decomposition with MECE Validation

```
FUNCTION decompose_query(query, triggered_agents):
    // Breaks complex query into sub-questions for each agent
    // Returns list of {question: str, target_agents: list[str]}
    
    // Use LLM to generate sub-questions
    decomposition_prompt = "Break down this query into specific sub-questions for: " + JOIN(triggered_agents, ", ")
    sub_questions_raw = invoke_llm(decomposition_prompt + "\n\nQuery: " + query)
    
    // Parse structured output
    sub_questions = parse_subquestions(sub_questions_raw)
    
    RETURN sub_questions
END FUNCTION

FUNCTION validate_mece(sub_questions):
    // Validates that sub-questions are Mutually Exclusive and Collectively Exhaustive
    // Returns {is_valid: bool, gaps: list[str], overlaps: list[tuple]}
    
    validation_result = {
        "is_valid": True,
        "gaps": [],
        "overlaps": []
    }
    
    // Check for overlaps (Mutual Exclusivity)
    FOR i = 0 TO LENGTH(sub_questions) - 1:
        FOR j = i + 1 TO LENGTH(sub_questions) - 1:
            semantic_overlap = calculate_semantic_overlap(sub_questions[i], sub_questions[j])
            
            IF semantic_overlap > 0.75 THEN  // High overlap threshold
                validation_result.overlaps.ADD((sub_questions[i], sub_questions[j]))
                validation_result.is_valid = False
            END IF
        END FOR
    END FOR
    
    // Check for gaps (Collective Exhaustiveness)
    // Use LLM to identify if original query is fully covered
    coverage_check = invoke_llm("Does this set of sub-questions fully cover the original query? Identify gaps.\n\nOriginal: " + original_query + "\n\nSub-questions: " + JOIN(sub_questions))
    
    IF coverage_check.has_gaps THEN
        validation_result.gaps = coverage_check.identified_gaps
        validation_result.is_valid = False
    END IF
    
    RETURN validation_result
END FUNCTION

FUNCTION revise_for_mece(sub_questions, gaps, overlaps):
    // Revises sub-questions to ensure MECE property
    // Returns revised list of sub-questions
    
    revised_questions = sub_questions
    
    // Remove overlaps by merging similar questions
    FOR EACH (q1, q2) IN overlaps:
        merged_question = merge_questions(q1, q2)
        revised_questions.REMOVE(q1)
        revised_questions.REMOVE(q2)
        revised_questions.ADD(merged_question)
    END FOR
    
    // Add questions to cover gaps
    FOR EACH gap IN gaps:
        gap_question = generate_question_for_gap(gap)
        revised_questions.ADD(gap_question)
    END FOR
    
    RETURN revised_questions
END FUNCTION
```

---

## 2. ALL FIVE TENSION PROTOCOLS

### 2.1 Sovereign ↔ Economist Tension Protocol

```
FUNCTION resolve_sovereign_economist_tension(state, sovereign_position, economist_position):
    // Resolves tension between sovereignty requirements and economic viability
    // Maximum 4 iterations before escalation
    // Returns {resolved: bool, solution: dict, iterations: int, escalation_report: optional[dict]}
    
    iteration_count = 0
    max_iterations = 4
    resolution_achieved = False
    
    // Extract key parameters from positions
    sovereignty_requirement = sovereign_position.requirement  // e.g., "EU-only infrastructure"
    cost_premium = economist_position.cost_delta  // e.g., additional €200K/year
    
    WHILE iteration_count < max_iterations AND NOT resolution_achieved:
        iteration_count = iteration_count + 1
        
        // Step 1: Economist calculates Trust Premium potential
        trust_premium_analysis = calculate_trust_premium(
            european_market_preference_data,
            sovereignty_requirement,
            state.query_context
        )
        
        trust_premium_revenue = trust_premium_analysis.projected_revenue
        trust_premium_confidence = trust_premium_analysis.confidence
        
        // Step 2: Sovereign quantifies sovereignty risk
        sovereignty_risk = quantify_sovereignty_risk(
            sovereignty_requirement,
            state.query_context
        )
        
        risk_probability = sovereignty_risk.probability  // e.g., 0.15 (15% chance of data breach/subpoena)
        risk_impact = sovereignty_risk.financial_impact  // e.g., €500K
        risk_mitigation_value = risk_probability * risk_impact
        
        // Step 3: Compare combined value vs cost delta
        combined_value = trust_premium_revenue + risk_mitigation_value
        
        IF combined_value > cost_premium THEN
            // Sovereign approach justified
            resolution_achieved = True
            solution = {
                "approach": "sovereign",
                "rationale": "Trust premium (€" + trust_premium_revenue + ") + Risk mitigation (€" + risk_mitigation_value + ") exceeds cost delta (€" + cost_premium + ")",
                "confidence": MIN(trust_premium_confidence, sovereignty_risk.confidence),
                "sovereign_rating": "ACCEPT",
                "economist_rating": "ACCEPT"
            }
        ELSE IF cost_premium > combined_value THEN
            // Cost delta too high, need hybrid architecture
            
            // Step 4: Architect proposes hybrid architecture
            hybrid_proposal = invoke_agent("Architect", {
                "task": "design_hybrid_architecture",
                "sovereignty_requirement": sovereignty_requirement,
                "cost_constraint": cost_premium,
                "acceptable_cost_delta": combined_value
            })
            
            // Evaluate hybrid proposal
            sovereign_rating = invoke_agent("Sovereign", {
                "task": "rate_proposal",
                "proposal": hybrid_proposal
            })
            
            economist_rating = invoke_agent("Economist", {
                "task": "rate_proposal",
                "proposal": hybrid_proposal
            })
            
            IF sovereign_rating.rating IN ["ACCEPT", "ENDORSE"] AND economist_rating.rating IN ["ACCEPT", "ENDORSE"] THEN
                resolution_achieved = True
                solution = {
                    "approach": "hybrid",
                    "architecture": hybrid_proposal,
                    "rationale": "Hybrid balances sovereignty and cost",
                    "sovereign_rating": sovereign_rating.rating,
                    "economist_rating": economist_rating.rating,
                    "confidence": MIN(sovereign_rating.confidence, economist_rating.confidence)
                }
            ELSE
                // Refine hybrid proposal for next iteration
                IF iteration_count < max_iterations THEN
                    // Provide feedback for refinement
                    hybrid_proposal = refine_proposal(
                        hybrid_proposal,
                        sovereign_rating.critique,
                        economist_rating.critique
                    )
                END IF
            END IF
        END IF
        
        // Update state with iteration progress
        UPDATE_STATE(state, {
            "tension_iterations": {
                "Sovereign_Economist": iteration_count
            },
            "current_iteration_result": {
                "trust_premium": trust_premium_revenue,
                "risk_mitigation": risk_mitigation_value,
                "cost_delta": cost_premium,
                "hybrid_proposal": hybrid_proposal IF EXISTS
            }
        })
    END WHILE
    
    // Check if resolution achieved
    IF NOT resolution_achieved THEN
        // Escalate to human with quantified trade-offs
        escalation_report = {
            "tension": "Sovereign ↔ Economist",
            "iterations_attempted": iteration_count,
            "sovereign_demand": sovereignty_requirement,
            "cost_delta": "€" + cost_premium + "/year",
            "trust_premium_potential": "€" + trust_premium_revenue + "/year",
            "risk_mitigation_value": "€" + risk_mitigation_value,
            "net_cost": "€" + (cost_premium - combined_value) + "/year",
            "recommendation": "Human decision required: accept net cost for sovereignty or compromise requirements"
        }
        
        RETURN {
            "resolved": False,
            "iterations": iteration_count,
            "escalation_report": escalation_report
        }
    ELSE
        RETURN {
            "resolved": True,
            "solution": solution,
            "iterations": iteration_count
        }
    END IF
END FUNCTION

FUNCTION calculate_trust_premium(market_data, sovereignty_requirement, context):
    // Calculates projected revenue increase from European market trust premium
    // Returns {projected_revenue: float, confidence: float}
    
    // Retrieve historical cases with similar sovereignty positioning
    similar_cases = retrieve_from_memory({
        "query": "European trust premium for " + sovereignty_requirement,
        "filter": "outcome.status == 'implemented'",
        "top_k": 5
    })
    
    IF LENGTH(similar_cases) > 0 THEN
        // Calculate average trust premium from historical data
        trust_premium_samples = []
        FOR EACH case IN similar_cases:
            IF case.outcome.trust_premium_measured EXISTS THEN
                trust_premium_samples.ADD(case.outcome.trust_premium_measured)
            END IF
        END FOR
        
        IF LENGTH(trust_premium_samples) > 0 THEN
            avg_premium = AVERAGE(trust_premium_samples)
            confidence = 0.8  // High confidence from historical data
        ELSE
            // No measured data, use market survey estimates
            avg_premium = estimate_from_market_surveys(context)
            confidence = 0.5  // Medium confidence from estimates
        END IF
    ELSE
        // No historical data, use baseline estimates
        avg_premium = estimate_from_market_surveys(context)
        confidence = 0.3  // Low confidence, no historical precedent
    END IF
    
    RETURN {
        "projected_revenue": avg_premium,
        "confidence": confidence
    }
END FUNCTION

FUNCTION quantify_sovereignty_risk(requirement, context):
    // Quantifies financial risk of NOT implementing sovereignty requirement
    // Returns {probability: float, financial_impact: float, confidence: float}
    
    // Use knowledge base to identify relevant risks
    risk_knowledge = retrieve_knowledge({
        "domain": "sovereignty_risks",
        "requirement": requirement
    })
    
    // Historical breach probability for non-sovereign architectures
    breach_probability = risk_knowledge.historical_breach_rate  // e.g., 0.15
    
    // Estimate financial impact
    IF context.industry IN ["healthcare", "finance", "government"] THEN
        // High-sensitivity industries
        avg_impact = 750000  // €750K average
    ELSE
        avg_impact = 500000  // €500K average
    END IF
    
    // Adjust for company size
    IF context.company_size == "SME" THEN
        financial_impact = avg_impact * 0.5
    ELSE IF context.company_size == "Large" THEN
        financial_impact = avg_impact * 1.5
    ELSE
        financial_impact = avg_impact
    END IF
    
    RETURN {
        "probability": breach_probability,
        "financial_impact": financial_impact,
        "confidence": 0.7  // Based on historical data quality
    }
END FUNCTION
```

### 2.2 Eco-System ↔ Architect Tension Protocol

```
FUNCTION resolve_ecosystem_architect_tension(state, ecosystem_position, architect_position):
    // Resolves tension between environmental constraints and technical solutions
    // Maximum 3 iterations before requiring Economist justification
    // Returns {resolved: bool, solution: dict, iterations: int, economist_justification: optional[dict]}
    
    iteration_count = 0
    max_iterations = 3
    resolution_achieved = False
    
    // Extract key parameters
    proposed_solution = architect_position.technical_solution
    sci_degradation = ecosystem_position.sci_degradation_percent  // e.g., 150%
    
    WHILE iteration_count < max_iterations AND NOT resolution_achieved:
        iteration_count = iteration_count + 1
        
        // Step 1: Eco-System provides specific SCI calculation
        sci_calculation = calculate_sci_score(
            proposed_solution,
            state.query_context
        )
        
        baseline_sci = sci_calculation.baseline
        proposed_sci = sci_calculation.proposed
        degradation_percent = ((proposed_sci - baseline_sci) / baseline_sci) * 100
        
        // Step 2: Architect proposes carbon mitigation strategies
        mitigation_strategies = propose_carbon_mitigation(
            proposed_solution,
            sci_calculation
        )
        
        // Calculate mitigated SCI
        mitigated_sci = apply_mitigation_to_sci(proposed_sci, mitigation_strategies)
        mitigated_degradation = ((mitigated_sci - baseline_sci) / baseline_sci) * 100
        
        // Step 3: Evaluate against threshold
        IF mitigated_degradation < 50 THEN
            // Acceptable with mitigation and monitoring
            resolution_achieved = True
            solution = {
                "approach": "original_with_mitigation",
                "technical_solution": proposed_solution,
                "mitigation_strategies": mitigation_strategies,
                "sci_baseline": baseline_sci,
                "sci_mitigated": mitigated_sci,
                "degradation_percent": mitigated_degradation,
                "monitoring_required": True,
                "ecosystem_rating": "ACCEPT",
                "architect_rating": "ACCEPT",
                "confidence": MIN(sci_calculation.confidence, 0.8)
            }
        ELSE IF mitigated_degradation >= 50 AND mitigated_degradation < 100 THEN
            // Borderline case - need alternative approach
            
            // Step 4: Architect proposes alternative approach
            alternative_solution = invoke_agent("Architect", {
                "task": "design_low_carbon_alternative",
                "original_solution": proposed_solution,
                "carbon_budget": baseline_sci * 1.5,  // Max 50% degradation
                "functional_requirements": state.query_context.requirements
            })
            
            // Re-calculate SCI for alternative
            alternative_sci_calc = calculate_sci_score(alternative_solution, state.query_context)
            alternative_degradation = ((alternative_sci_calc.proposed - baseline_sci) / baseline_sci) * 100
            
            IF alternative_degradation < 50 THEN
                resolution_achieved = True
                solution = {
                    "approach": "alternative_design",
                    "technical_solution": alternative_solution,
                    "sci_baseline": baseline_sci,
                    "sci_proposed": alternative_sci_calc.proposed,
                    "degradation_percent": alternative_degradation,
                    "ecosystem_rating": "ACCEPT",
                    "architect_rating": "ACCEPT",
                    "rationale": "Alternative design meets carbon budget",
                    "confidence": alternative_sci_calc.confidence
                }
            END IF
        ELSE
            // SCI degradation >100% - cannot resolve architecturally
            // Will require Economist justification after loop
        END IF
        
        // Update state
        UPDATE_STATE(state, {
            "tension_iterations": {
                "EcoSystem_Architect": iteration_count
            },
            "sci_analysis": {
                "baseline": baseline_sci,
                "original_proposed": proposed_sci,
                "mitigated": mitigated_sci,
                "alternative": alternative_sci_calc.proposed IF EXISTS,
                "mitigation_strategies": mitigation_strategies
            }
        })
    END WHILE
    
    IF NOT resolution_achieved THEN
        // Step 5: Require Economist to justify business value exceeding carbon cost
        economist_justification = invoke_agent("Economist", {
            "task": "justify_carbon_cost",
            "carbon_degradation_percent": degradation_percent,
            "business_value": state.query_context.business_value,
            "alternative_options": state.sci_analysis.alternative IF EXISTS
        })
        
        // Evaluate justification
        IF economist_justification.rating == "ENDORSE" AND economist_justification.business_value_multiple > 3.0 THEN
            // Business value >3x carbon cost - acceptable with disclosure
            solution = {
                "approach": "high_carbon_with_justification",
                "technical_solution": proposed_solution,
                "sci_degradation_percent": degradation_percent,
                "business_justification": economist_justification,
                "ecosystem_rating": "WARN",
                "architect_rating": "ACCEPT",
                "economist_rating": "ENDORSE",
                "disclosure_required": True,
                "rationale": "Business value justifies carbon cost, but requires transparency"
            }
            
            RETURN {
                "resolved": True,
                "solution": solution,
                "iterations": iteration_count,
                "economist_justification": economist_justification
            }
        ELSE
            // Cannot justify - recommend blocking
            RETURN {
                "resolved": False,
                "iterations": iteration_count,
                "recommendation": "BLOCK - SCI degradation exceeds acceptable limits and business value insufficient"
            }
        END IF
    ELSE
        RETURN {
            "resolved": True,
            "solution": solution,
            "iterations": iteration_count
        }
    END IF
END FUNCTION

FUNCTION calculate_sci_score(solution, context):
    // Calculates Software Carbon Intensity using SCI = ((E × I) + M) / R
    // E = Energy consumed, I = Carbon intensity, M = Embodied emissions, R = Functional unit
    // Returns {baseline: float, proposed: float, confidence: float}
    
    // Retrieve baseline SCI from context or memory
    IF context.baseline_sci EXISTS THEN
        baseline_sci = context.baseline_sci
    ELSE
        // Estimate baseline from industry standards
        baseline_sci = estimate_baseline_sci(context.industry, context.workload_type)
    END IF
    
    // Cold-start handling: use industry standard if no baseline available
    IF baseline_sci == NULL THEN
        baseline_sci = 50.0  // Industry standard gCO2e/request
        LOG("No baseline SCI available, using industry standard of 50.0 gCO2e/request")
    END IF
    
    // Calculate proposed SCI
    // E = Energy (kWh)
    energy_kwh = estimate_energy_consumption(solution.compute_requirements, solution.runtime_hours)
    
    // I = Carbon intensity (gCO2eq/kWh) - depends on region
    carbon_intensity = get_grid_carbon_intensity(solution.deployment_region)
    
    // M = Embodied emissions (gCO2eq) - hardware manufacturing
    embodied_carbon = estimate_embodied_carbon(solution.hardware_requirements)
    
    // R = Functional unit (e.g., per request, per user)
    functional_unit = solution.expected_usage_volume
    
    proposed_sci = ((energy_kwh * carbon_intensity) + embodied_carbon) / functional_unit
    
    RETURN {
        "baseline": baseline_sci,
        "proposed": proposed_sci,
        "confidence": 0.7,  // Based on estimation accuracy
        "breakdown": {
            "energy_kwh": energy_kwh,
            "carbon_intensity": carbon_intensity,
            "embodied_carbon": embodied_carbon,
            "functional_unit": functional_unit
        }
    }
END FUNCTION

FUNCTION propose_carbon_mitigation(solution, sci_calculation):
    // Proposes strategies to reduce carbon impact
    // Returns list of mitigation strategies with estimated SCI reduction
    
    strategies = []
    
    // Strategy 1: Carbon-aware scheduling
    IF solution.can_defer_workload THEN
        strategies.ADD({
            "name": "carbon_aware_scheduling",
            "description": "Schedule compute during low-grid-carbon periods",
            "sci_reduction_percent": 15,
            "implementation_cost": "low"
        })
    END IF
    
    // Strategy 2: Hardware efficiency improvements
    IF solution.compute_requirements.can_optimize THEN
        strategies.ADD({
            "name": "hardware_optimization",
            "description": "Use more efficient processors or GPU alternatives",
            "sci_reduction_percent": 20,
            "implementation_cost": "medium"
        })
    END IF
    
    // Strategy 3: Algorithm optimization
    strategies.ADD({
        "name": "algorithm_optimization",
        "description": "Reduce computational complexity through algorithmic improvements",
        "sci_reduction_percent": 25,
        "implementation_cost": "high"
    })
    
    // Strategy 4: Renewable energy procurement
    IF solution.deployment_region.renewable_energy_available THEN
        strategies.ADD({
            "name": "renewable_energy",
            "description": "Deploy in regions with high renewable energy grid mix",
            "sci_reduction_percent": 30,
            "implementation_cost": "low"
        })
    END IF
    
    // Strategy 5: Carbon offsets (last resort)
    strategies.ADD({
        "name": "carbon_offsets",
        "description": "Purchase verified carbon offsets",
        "sci_reduction_percent": 100,  // On paper, but doesn't reduce actual emissions
        "implementation_cost": "medium",
        "note": "Does not reduce actual emissions, only offsets"
    })
    
    RETURN strategies
END FUNCTION
```

### 2.3 Jurist ↔ Philosopher Tension Protocol

```
FUNCTION resolve_jurist_philosopher_tension(state, jurist_position, philosopher_position):
    // Resolves tension between legal compliance and ethical principles
    // NO ITERATION LIMIT - Instant escalation to human for values conflicts
    // Returns {resolved: False, escalation_report: dict}
    
    // This tension represents a fundamental values conflict that requires human judgment
    // System does NOT attempt automatic resolution
    
    // Generate comprehensive ethics vs. legal compliance report
    escalation_report = {
        "tension": "Jurist ↔ Philosopher (Values Conflict)",
        "instant_escalation": True,
        
        "legal_position": {
            "rating": jurist_position.rating,  // Should be "ACCEPT"
            "compliance_met": jurist_position.compliance_requirements_met,
            "legal_basis": jurist_position.legal_basis,
            "risk_level": jurist_position.legal_risk,
            "relevant_regulations": jurist_position.applicable_laws
        },
        
        "ethical_position": {
            "rating": philosopher_position.rating,  // Should be "BLOCK" or "WARN"
            "violated_principles": philosopher_position.constitutional_violations,
            "harm_analysis": philosopher_position.harm_assessment,
            "trust_capital_impact": philosopher_position.trust_impact,
            "long_term_consequences": philosopher_position.long_term_analysis
        },
        
        "historical_precedents": retrieve_similar_ethical_dilemmas(state.query),
        
        "decision_framework": {
            "question": "Does ethical alignment override legal minimum compliance?",
            "considerations": [
                "Legal compliance satisfies regulatory requirements but violates organizational values",
                "Short-term legal safety vs. long-term reputation and trust",
                "Competitive pressure vs. ethical standards",
                "Stakeholder expectations and brand positioning"
            ]
        },
        
        "recommendation": "HUMAN DECISION REQUIRED - This represents a values hierarchy question that cannot be algorithmically resolved. Legal minimum is met, but ethical standards are violated. Leadership must decide which takes precedence in this context."
    }
    
    // Update state with escalation
    UPDATE_STATE(state, {
        "tension_type": "values_conflict",
        "escalation_required": True,
        "escalation_reason": "Jurist-Philosopher disagreement on legal vs. ethical standards",
        "escalation_report": escalation_report
    })
    
    // Always return unresolved with escalation report
    RETURN {
        "resolved": False,
        "escalation_report": escalation_report,
        "requires_human_decision": True
    }
END FUNCTION

FUNCTION retrieve_similar_ethical_dilemmas(query):
    // Retrieves historical cases with similar ethical tensions
    // Returns list of precedent cases with outcomes
    
    ethical_query_embedding = generate_query_embedding(query + " ethical dilemma legal compliance")
    
    similar_cases = retrieve_from_memory({
        "embedding": ethical_query_embedding,
        "filter": "tension_type == 'Jurist_Philosopher'",
        "top_k": 3
    })
    
    precedents = []
    FOR EACH case IN similar_cases:
        precedents.ADD({
            "case_summary": case.query,
            "legal_position": case.jurist_rating,
            "ethical_position": case.philosopher_rating,
            "human_decision": case.outcome.decision,
            "decision_rationale": case.outcome.rationale,
            "long_term_result": case.outcome.long_term_impact IF EXISTS
        })
    END FOR
    
    RETURN precedents
END FUNCTION
```

### 2.4 Operator ↔ Strategy Agents Tension Protocol

```
FUNCTION resolve_operator_strategy_tension(state, operator_position, strategy_positions):
    // Resolves tension between strategic vision and operational reality
    // Maximum 2 iterations before requiring scope reduction
    // Returns {resolved: bool, solution: dict, iterations: int}
    
    iteration_count = 0
    max_iterations = 2
    resolution_achieved = False
    
    // Extract key parameters
    strategic_timeline = extract_assumed_timeline(strategy_positions)
    operational_timeline = operator_position.realistic_timeline
    timeline_gap = operational_timeline - strategic_timeline
    timeline_gap_percent = (timeline_gap / strategic_timeline) * 100
    
    WHILE iteration_count < max_iterations AND NOT resolution_achieved:
        iteration_count = iteration_count + 1
        
        // Step 1: Operator provides detailed execution breakdown
        execution_breakdown = generate_execution_breakdown(
            strategy_positions,
            state.query_context
        )
        
        breakdown_phases = {
            "recruitment": execution_breakdown.recruitment_timeline,
            "training": execution_breakdown.training_timeline,
            "procurement": execution_breakdown.procurement_timeline,
            "integration": execution_breakdown.integration_timeline,
            "stabilization": execution_breakdown.stabilization_timeline
        }
        
        // Step 2: Strategy agents must choose response path
        IF timeline_gap_percent > 200 THEN
            // Gap too large (>3x), must revise fundamentally
            
            // Option A: Revise timeline
            revised_timeline = operational_timeline
            
            // Option B: Reduce scope to fit timeline
            reduced_scope = calculate_reduced_scope(
                strategy_positions,
                strategic_timeline,
                execution_breakdown
            )
            
            // Option C: Increase resources
            increased_resources = calculate_resource_increase(
                strategic_timeline,
                operational_timeline,
                execution_breakdown
            )
            
            // Present options to strategy agents
            // strategy_agents = agents who contributed to original timeline
            // Dynamically determined from state.agent_responses where timeline_estimate exists
            // Typically: Economist (ROI timeline), Architect (build timeline), Futurist (risk timeline)
            strategy_choice = invoke_strategy_agents_for_choice({
                "option_a": {
                    "approach": "extend_timeline",
                    "new_timeline": revised_timeline,
                    "impact": "Delayed business value realization"
                },
                "option_b": {
                    "approach": "reduce_scope",
                    "reduced_scope": reduced_scope,
                    "impact": "Limited initial functionality, phased rollout"
                },
                "option_c": {
                    "approach": "increase_resources",
                    "additional_resources": increased_resources,
                    "impact": "Higher cost, faster delivery"
                }
            })
            
            selected_option = strategy_choice.selected
            
        ELSE
            // Gap manageable (<2x), can adjust
            
            // Propose timeline revision with mitigation
            revised_strategy = {
                "timeline": operational_timeline,
                "mitigation": propose_timeline_mitigation(timeline_gap, execution_breakdown)
            }
            
            selected_option = "revise_timeline_with_mitigation"
        END IF
        
        // Step 3: Economist re-evaluates ROI with realistic timeline
        roi_analysis = invoke_agent("Economist", {
            "task": "recalculate_roi",
            "revised_timeline": revised_timeline IF selected_option == "extend_timeline",
            "reduced_scope": reduced_scope IF selected_option == "reduce_scope",
            "increased_resources": increased_resources IF selected_option == "increase_resources",
            "original_business_case": state.query_context.business_case
        })
        
        // Step 4: Check if revised business case is still positive
        IF roi_analysis.roi_positive AND roi_analysis.payback_period < 3 THEN
            // Acceptable revised plan
            resolution_achieved = True
            solution = {
                "approach": selected_option,
                "revised_timeline": revised_timeline IF EXISTS,
                "reduced_scope": reduced_scope IF EXISTS,
                "increased_resources": increased_resources IF EXISTS,
                "execution_breakdown": breakdown_phases,
                "revised_roi": roi_analysis,
                "operator_rating": "ACCEPT",
                "economist_rating": roi_analysis.rating,
                "confidence": MIN(operator_position.confidence, roi_analysis.confidence)
            }
        ELSE
            // Business case no longer viable with realistic timeline
            IF iteration_count < max_iterations THEN
                // Try alternative approach in next iteration
                // Request strategy agents to reconsider scope or approach
            ELSE
                // Exceeded iterations, must reject or escalate
                resolution_achieved = False
            END IF
        END IF
        
        // Update state
        UPDATE_STATE(state, {
            "tension_iterations": {
                "Operator_Strategy": iteration_count
            },
            "execution_analysis": {
                "strategic_timeline": strategic_timeline,
                "operational_timeline": operational_timeline,
                "timeline_gap_percent": timeline_gap_percent,
                "breakdown": breakdown_phases,
                "selected_option": selected_option,
                "revised_roi": roi_analysis
            }
        })
    END WHILE
    
    IF NOT resolution_achieved THEN
        // Proposal rejected - no viable execution path
        RETURN {
            "resolved": False,
            "iterations": iteration_count,
            "recommendation": "REJECT - No viable execution path that maintains positive business case",
            "details": {
                "timeline_gap": timeline_gap_percent + "%",
                "roi_with_realistic_timeline": roi_analysis.roi IF EXISTS
            }
        }
    ELSE
        RETURN {
            "resolved": True,
            "solution": solution,
            "iterations": iteration_count
        }
    END IF
END FUNCTION

FUNCTION generate_execution_breakdown(strategy_positions, context):
    // Generates realistic timeline breakdown for implementation
    // Returns detailed phase timeline estimates
    
    // Recruitment timeline
    IF context.requires_new_skills THEN
        recruitment_months = 6  // 6 months to find qualified candidates
    ELSE
        recruitment_months = 0  // Use existing team
    END IF
    
    // Training timeline
    training_months = estimate_training_duration(context.skill_requirements, context.team_experience)
    
    // Procurement timeline
    IF context.requires_procurement THEN
        procurement_months = 3  // RFP to contract average
    ELSE
        procurement_months = 0
    END IF
    
    // Integration timeline
    integration_months = estimate_integration_complexity(context.legacy_systems, context.technical_scope)
    
    // Stabilization timeline
    stabilization_months = 3  // Standard stabilization period
    
    total_months = recruitment_months + training_months + procurement_months + integration_months + stabilization_months
    
    RETURN {
        "recruitment_timeline": recruitment_months + " months",
        "training_timeline": training_months + " months",
        "procurement_timeline": procurement_months + " months",
        "integration_timeline": integration_months + " months",
        "stabilization_timeline": stabilization_months + " months",
        "total_timeline": total_months + " months"
    }
END FUNCTION
```

### 2.5 Futurist ↔ All Agents Tension Protocol

```
FUNCTION resolve_futurist_all_agents_tension(state, futurist_position, all_agent_positions):
    // Resolves tension when strategy fails in >50% of plausible future scenarios
    // Maximum 3 iterations before requiring strategic optionality analysis
    // Returns {resolved: bool, solution: dict, iterations: int, scenario_robustness: dict}
    
    iteration_count = 0
    max_iterations = 3
    resolution_achieved = False
    
    // Extract scenario analysis from Futurist
    scenario_matrix = futurist_position.scenario_matrix
    failure_rate = futurist_position.scenario_failure_rate  // e.g., 0.65 (65% scenarios fail)
    
    WHILE iteration_count < max_iterations AND NOT resolution_achieved:
        iteration_count = iteration_count + 1
        
        // Step 1: Futurist defines scenario matrix (2-4 key uncertainties)
        IF iteration_count == 1 THEN
            scenario_matrix = define_scenario_matrix(state.query_context)
        END IF
        
        // Scenario matrix structure:
        // {
        //   "uncertainties": ["EU regulation", "Technology costs"],
        //   "scenarios": [
        //     {"name": "Strict regulation + High costs", "probability": 0.25},
        //     {"name": "Strict regulation + Low costs", "probability": 0.25},
        //     {"name": "Loose regulation + High costs", "probability": 0.25},
        //     {"name": "Loose regulation + Low costs", "probability": 0.25}
        //   ]
        // }
        
        // Step 2: All agents re-evaluate proposal under each scenario
        scenario_evaluations = {}
        
        FOR EACH scenario IN scenario_matrix.scenarios:
            scenario_context = {
                "original_context": state.query_context,
                "scenario_assumptions": scenario.assumptions
            }
            
            // Invoke each agent to evaluate under this scenario
            scenario_ratings = {}
            FOR EACH agent IN all_agent_positions:
                agent_scenario_rating = invoke_agent(agent.id, {
                    "task": "evaluate_under_scenario",
                    "proposal": state.current_proposal,
                    "scenario": scenario_context
                })
                scenario_ratings[agent.id] = agent_scenario_rating
            END FOR
            
            // Check if proposal succeeds in this scenario
            scenario_success = check_convergence(scenario_ratings)
            
            scenario_evaluations[scenario.name] = {
                "success": scenario_success.converged,
                "probability": scenario.probability,
                "ratings": scenario_ratings,
                "failure_reason": scenario_success.failure_reason IF NOT scenario_success.converged
            }
        END FOR
        
        // Step 3: Calculate weighted scenario robustness score
        weighted_success_rate = 0
        FOR EACH scenario_name, evaluation IN scenario_evaluations:
            IF evaluation.success THEN
                weighted_success_rate = weighted_success_rate + evaluation.probability
            END IF
        END FOR
        
        // Step 4: Evaluate against acceptance threshold
        IF weighted_success_rate >= 0.60 THEN
            // Strategy robust across >60% of probability-weighted scenarios
            resolution_achieved = True
            solution = {
                "approach": "scenario_robust",
                "weighted_success_rate": weighted_success_rate,
                "scenario_evaluations": scenario_evaluations,
                "futurist_rating": "ACCEPT",
                "recommendation": "Strategy succeeds in majority of plausible futures",
                "confidence": 0.75
            }
        ELSE
            // Strategy fails in too many scenarios - need adaptation mechanisms
            
            // Step 5: Architect designs adaptation mechanisms
            adaptation_design = invoke_agent("Architect", {
                "task": "design_modular_architecture",
                "failing_scenarios": extract_failing_scenarios(scenario_evaluations),
                "success_scenarios": extract_success_scenarios(scenario_evaluations),
                "adaptation_requirements": identify_adaptation_points(scenario_matrix)
            })
            
            // Modular architecture should allow for:
            // - Component substitution based on scenario realization
            // - Gradual rollout with scenario monitoring
            // - Pivot points with predefined decision criteria
            
            // Re-evaluate with adaptation mechanisms
            adapted_success_rate = estimate_success_with_adaptation(
                scenario_evaluations,
                adaptation_design
            )
            
            IF adapted_success_rate >= 0.60 THEN
                resolution_achieved = True
                solution = {
                    "approach": "adaptive_architecture",
                    "base_strategy": state.current_proposal,
                    "adaptation_mechanisms": adaptation_design,
                    "weighted_success_rate": adapted_success_rate,
                    "scenario_evaluations": scenario_evaluations,
                    "futurist_rating": "ACCEPT",
                    "architect_rating": "ACCEPT",
                    "monitoring_required": True,
                    "pivot_points": adaptation_design.pivot_points,
                    "confidence": 0.70
                }
            ELSE
                // Even with adaptation, insufficient robustness
                IF iteration_count < max_iterations THEN
                    // Refine adaptation design or reconsider base strategy
                    state.current_proposal = request_strategy_revision(
                        state.current_proposal,
                        scenario_evaluations,
                        "insufficient_scenario_robustness"
                    )
                END IF
            END IF
        END IF
        
        // Update state
        UPDATE_STATE(state, {
            "tension_iterations": {
                "Futurist_All": iteration_count
            },
            "scenario_analysis": {
                "matrix": scenario_matrix,
                "evaluations": scenario_evaluations,
                "weighted_success_rate": weighted_success_rate,
                "adaptation_design": adaptation_design IF EXISTS
            }
        })
    END WHILE
    
    IF NOT resolution_achieved THEN
        // Strategy is too brittle for uncertain future
        RETURN {
            "resolved": False,
            "iterations": iteration_count,
            "recommendation": "BLOCK - Strategy fails in >40% of probability-weighted scenarios and cannot be adequately adapted",
            "scenario_robustness": {
                "success_rate": weighted_success_rate,
                "failing_scenarios": extract_failing_scenarios(scenario_evaluations),
                "required_improvements": "Strategy requires fundamental redesign for future robustness"
            }
        }
    ELSE
        RETURN {
            "resolved": True,
            "solution": solution,
            "iterations": iteration_count,
            "scenario_robustness": {
                "success_rate": weighted_success_rate,
                "scenario_matrix": scenario_matrix,
                "adaptation_mechanisms": solution.adaptation_mechanisms IF EXISTS
            }
        }
    END IF
END FUNCTION

FUNCTION define_scenario_matrix(context):
    // Defines 2-4 key uncertainties and generates scenario combinations
    // Returns scenario matrix structure
    
    // Identify key uncertainties relevant to context
    uncertainties = []
    
    // Always consider regulatory uncertainty for EU context
    uncertainties.ADD({
        "dimension": "EU Regulation",
        "states": ["Strict enforcement", "Moderate enforcement", "Loose enforcement"]
    })
    
    // Technology cost uncertainty
    uncertainties.ADD({
        "dimension": "Technology Costs",
        "states": ["Costs decrease 10x", "Costs stable", "Costs increase"]
    })
    
    // Geopolitical uncertainty (if relevant)
    IF context.has_cross_border_dependencies THEN
        uncertainties.ADD({
            "dimension": "Geopolitical",
            "states": ["EU-US alignment", "Decoupling", "Fragmentation"]
        })
    END IF
    
    // Generate scenario combinations
    scenarios = generate_scenario_combinations(uncertainties)
    
    // Assign probabilities using Futurist's trend analysis
    // Futurist assigns initial probabilities based on trend analysis
    FOR EACH scenario IN scenarios:
        scenario.probability = Futurist.ESTIMATE_PROBABILITY(scenario)
    END FOR
    
    // Validate and normalize probabilities to ensure they sum to 1.0
    total_prob = SUM(all scenario.probability)
    IF total_prob != 1.0 THEN
        FOR EACH scenario IN scenarios:
            scenario.probability = scenario.probability / total_prob
        END FOR
        LOG("Normalized scenario probabilities to sum to 1.0")
    END IF
    
    RETURN {
        "uncertainties": uncertainties,
        "scenarios": scenarios,
        "time_horizon": "3-5 years"
    }
END FUNCTION

FUNCTION estimate_success_with_adaptation(scenario_evaluations, adaptation_design):
    // Estimates improved success rate with adaptation mechanisms
    // Returns weighted success rate with adaptation
    
    improved_rate = 0
    
    FOR EACH scenario_name, evaluation IN scenario_evaluations:
        IF evaluation.success THEN
            // Already succeeds, no change
            improved_rate = improved_rate + evaluation.probability
        ELSE
            // Check if adaptation mechanisms address failure reason
            IF adaptation_design.addresses_failure(evaluation.failure_reason) THEN
                // Assume 70% chance adaptation resolves issue
                improved_rate = improved_rate + (evaluation.probability * 0.7)
            END IF
        END IF
    END FOR
    
    RETURN improved_rate
END FUNCTION
```

---

## 3. CONVERGENCE TESTING ALGORITHM

```
FUNCTION check_convergence(agent_ratings, state):
    // Tests whether debate has reached convergence based on cumulative criteria
    // ALL criteria must be met simultaneously
    // Returns {converged: bool, status: str, details: dict}
    
    convergence_result = {
        "converged": False,
        "status": "",
        "details": {},
        "failed_criteria": []
    }
    
    // Extract ratings and confidence from all engaged agents
    all_ratings = []
    all_confidences = []
    warn_ratings = []
    
    FOR EACH agent_id, rating_data IN agent_ratings:
        all_ratings.ADD(rating_data.rating)
        all_confidences.ADD(rating_data.confidence)
        
        IF rating_data.rating == "WARN" THEN
            warn_ratings.ADD({
                "agent": agent_id,
                "rating_data": rating_data
            })
        END IF
    END FOR
    
    total_agents = LENGTH(all_ratings)
    
    // ========================================
    // CRITERION 1: Zero BLOCK ratings
    // ========================================
    block_count = COUNT(all_ratings WHERE rating == "BLOCK")
    
    IF block_count > 0 THEN
        convergence_result.failed_criteria.ADD("blocking_concerns")
        convergence_result.details["block_count"] = block_count
        convergence_result.details["blocking_agents"] = extract_agents_with_rating(agent_ratings, "BLOCK")
        convergence_result.status = "BLOCKED: " + block_count + " agent(s) have blocking concerns that must be resolved"
        RETURN convergence_result
    END IF
    
    // ========================================
    // CRITERION 2: Maximum 2 WARN ratings
    // ========================================
    warn_count = LENGTH(warn_ratings)
    
    IF warn_count > 2 THEN
        convergence_result.failed_criteria.ADD("too_many_warnings")
        convergence_result.details["warn_count"] = warn_count
        convergence_result.details["warning_agents"] = extract_agents_with_rating(agent_ratings, "WARN")
        convergence_result.status = "TOO MANY WARNINGS: " + warn_count + " warnings exceed maximum of 2"
        RETURN convergence_result
    END IF
    
    // ========================================
    // CRITERION 3: All WARN ratings must have accepted mitigation plans
    // ========================================
    IF warn_count > 0 THEN
        FOR EACH warn_entry IN warn_ratings:
            agent_id = warn_entry.agent
            rating_data = warn_entry.rating_data
            
            // Check if mitigation plan exists
            IF rating_data.mitigation_plan IS NULL OR rating_data.mitigation_plan == "" THEN
                convergence_result.failed_criteria.ADD("missing_mitigation")
                convergence_result.details["agent_without_mitigation"] = agent_id
                convergence_result.status = "WARN without mitigation plan from " + agent_id
                RETURN convergence_result
            END IF
            
            // Check if mitigation was accepted by the warning agent
            IF rating_data.mitigation_accepted != True THEN
                convergence_result.failed_criteria.ADD("mitigation_not_accepted")
                convergence_result.details["agent_rejected_mitigation"] = agent_id
                convergence_result.details["rejection_reason"] = rating_data.rejection_reason
                convergence_result.status = "Mitigation plan not accepted by " + agent_id
                RETURN convergence_result
            END IF
        END FOR
    END IF
    
    // ========================================
    // CRITERION 4: Combined confidence level >70%
    // ========================================
    average_confidence = AVERAGE(all_confidences)
    
    IF average_confidence <= 0.70 THEN
        convergence_result.failed_criteria.ADD("insufficient_confidence")
        convergence_result.details["average_confidence"] = average_confidence
        convergence_result.details["confidence_threshold"] = 0.70
        convergence_result.details["confidence_by_agent"] = compile_confidence_report(agent_ratings)
        convergence_result.status = "Insufficient combined confidence: " + (average_confidence * 100) + "% (requires >70%)"
        RETURN convergence_result
    END IF
    
    // ========================================
    // CRITERION 5: At least 60% ACCEPT or ENDORSE ratings
    // ========================================
    accept_or_endorse_count = COUNT(all_ratings WHERE rating IN ["ACCEPT", "ENDORSE"])
    acceptance_rate = accept_or_endorse_count / total_agents
    
    IF acceptance_rate < 0.60 THEN
        convergence_result.failed_criteria.ADD("insufficient_agreement")
        convergence_result.details["acceptance_rate"] = acceptance_rate
        convergence_result.details["accept_endorse_count"] = accept_or_endorse_count
        convergence_result.details["total_agents"] = total_agents
        convergence_result.details["rating_distribution"] = calculate_rating_distribution(all_ratings)
        convergence_result.status = "Insufficient agent agreement: " + (acceptance_rate * 100) + "% (requires ≥60%)"
        RETURN convergence_result
    END IF
    
    // ========================================
    // ALL CRITERIA PASSED - CONVERGENCE ACHIEVED
    // ========================================
    convergence_result.converged = True
    convergence_result.status = "CONVERGENCE ACHIEVED"
    convergence_result.details = {
        "total_agents": total_agents,
        "block_count": 0,
        "warn_count": warn_count,
        "accept_count": COUNT(all_ratings WHERE rating == "ACCEPT"),
        "endorse_count": COUNT(all_ratings WHERE rating == "ENDORSE"),
        "average_confidence": average_confidence,
        "acceptance_rate": acceptance_rate,
        "all_criteria_met": True
    }
    
    // Update state graph with convergence
    UPDATE_STATE(state, {
        "convergence_status": "achieved",
        "convergence_timestamp": current_timestamp(),
        "convergence_details": convergence_result.details
    })
    
    RETURN convergence_result
END FUNCTION

FUNCTION extract_agents_with_rating(agent_ratings, target_rating):
    // Extracts list of agent IDs that gave a specific rating
    // Returns list of {agent_id: str, reasoning: str}
    
    matching_agents = []
    
    FOR EACH agent_id, rating_data IN agent_ratings:
        IF rating_data.rating == target_rating THEN
            matching_agents.ADD({
                "agent_id": agent_id,
                "reasoning": rating_data.reasoning,
                "confidence": rating_data.confidence
            })
        END IF
    END FOR
    
    RETURN matching_agents
END FUNCTION

FUNCTION calculate_rating_distribution(all_ratings):
    // Calculates count and percentage of each rating type
    // Returns dict with distribution statistics
    
    distribution = {
        "BLOCK": 0,
        "WARN": 0,
        "ACCEPT": 0,
        "ENDORSE": 0
    }
    
    total = LENGTH(all_ratings)
    
    FOR EACH rating IN all_ratings:
        distribution[rating] = distribution[rating] + 1
    END FOR
    
    // Convert to percentages
    distribution_percent = {}
    FOR EACH rating_type, count IN distribution:
        distribution_percent[rating_type] = {
            "count": count,
            "percent": (count / total) * 100
        }
    END FOR
    
    RETURN distribution_percent
END FUNCTION

FUNCTION compile_confidence_report(agent_ratings):
    // Compiles confidence levels by agent for debugging low confidence issues
    // Returns sorted list of {agent: str, confidence: float}
    
    confidence_report = []
    
    FOR EACH agent_id, rating_data IN agent_ratings:
        confidence_report.ADD({
            "agent": agent_id,
            "confidence": rating_data.confidence,
            "rating": rating_data.rating
        })
    END FOR
    
    // Sort by confidence (lowest first to highlight problem areas)
    sorted_report = SORT(confidence_report BY confidence ASCENDING)
    
    RETURN sorted_report
END FUNCTION
```

---

## 4. MEMORY RETRIEVAL STRATEGY (Hybrid B+C)

```
FUNCTION retrieve_relevant_cases(query, state):
    // Retrieves relevant historical cases using Hybrid B+C approach
    // Combines immediate feedback with optional long-term outcome tracking
    // Returns {cases: list[Case], retrieval_metadata: dict}
    
    // Step 1: Generate query embedding
    query_embedding = generate_query_embedding(query)
    
    // Step 2: Vector similarity search in Chroma
    vector_search_results = vector_search_chroma({
        "embedding": query_embedding,
        "collection": "historical_cases",
        "top_k": 10,  // Retrieve more initially for filtering
        "similarity_threshold": 0.7
    })
    
    // Step 3: Filter by quality score (immediate feedback)
    filtered_cases = []
    confidence_penalty = 0  // Track quality degradation
    
    FOR EACH case IN vector_search_results:
        IF case.user_feedback.quality_score >= 3.5 THEN
            filtered_cases.ADD(case)
        END IF
    END FOR
    
    // If no high-quality cases exist, progressively lower threshold
    IF LENGTH(filtered_cases) == 0 THEN
        FOR EACH case IN vector_search_results:
            IF case.user_feedback.quality_score >= 3.0 THEN
                filtered_cases.ADD(case)
            END IF
        END FOR
        confidence_penalty = -0.20
        LOG("No cases with quality ≥3.5, lowered threshold to 3.0")
        
        IF LENGTH(filtered_cases) == 0 THEN
            FOR EACH case IN vector_search_results:
                IF case.user_feedback.quality_score >= 2.5 THEN
                    filtered_cases.ADD(case)
                END IF
            END FOR
            confidence_penalty = -0.25
            LOG("No cases with quality ≥3.0, lowered threshold to 2.5")
        END IF
    END IF
    
    // Step 4: Apply enhanced weighting for verified outcomes
    weighted_cases = []
    FOR EACH case IN filtered_cases:
        base_score = case.similarity_score  // From vector search
        
        // Apply outcome-based weighting if available
        IF case.outcome.status == "implemented" AND case.outcome.alignment_score >= 4.0 THEN
            // Boost cases with verified positive outcomes
            enhanced_score = base_score * 1.5  // 50% boost
            case.enhanced_score = enhanced_score
            case.boost_reason = "verified_positive_outcome"
        ELSE IF case.outcome.status == "implemented" AND case.outcome.alignment_score < 3.0 THEN
            // Penalize cases with poor outcomes
            enhanced_score = base_score * 0.7  // 30% penalty
            case.enhanced_score = enhanced_score
            case.boost_reason = "verified_negative_outcome"
        ELSE
            // No outcome data or not implemented - use immediate feedback only
            enhanced_score = base_score
            case.enhanced_score = enhanced_score
            case.boost_reason = "immediate_feedback_only"
        END IF
        
        weighted_cases.ADD(case)
    END FOR
    
    // Step 5: Re-rank by enhanced score
    sorted_cases = SORT(weighted_cases BY enhanced_score DESCENDING)
    
    // Step 6: Select top 3 for return
    top_cases = sorted_cases[0:3]
    
    // Step 7: Handle cold-start scenario (no similar cases)
    retrieval_metadata = {
        "total_matches": LENGTH(vector_search_results),
        "quality_filtered": LENGTH(filtered_cases),
        "returned": LENGTH(top_cases),
        "cold_start": False,
        "confidence_adjustment": confidence_penalty  // Includes progressive threshold penalty
    }
    
    IF LENGTH(top_cases) == 0 THEN
        // No sufficiently similar cases found
        retrieval_metadata.cold_start = True
        retrieval_metadata.confidence_adjustment = -0.15  // Reduce agent confidence by 15%
        retrieval_metadata.warning = "No historical precedent found. Recommendation based on principles only."
    ELSE IF top_cases[0].similarity_score < 0.75 THEN
        // Weak similarity
        retrieval_metadata.confidence_adjustment = MIN(confidence_penalty, -0.10)  // Use worse of two penalties
        retrieval_metadata.warning = "Limited historical precedent. Recommendation relies heavily on first principles."
    END IF
    
    // Step 8: Update state with retrieval info
    UPDATE_STATE(state, {
        "memory_retrieval": {
            "query": query,
            "cases_retrieved": top_cases,
            "metadata": retrieval_metadata,
            "timestamp": current_timestamp()
        }
    })
    
    RETURN {
        "cases": top_cases,
        "retrieval_metadata": retrieval_metadata
    }
END FUNCTION

FUNCTION store_new_case(state, final_recommendation, convergence_details):
    // Stores completed case in memory system for future retrieval
    // Captures immediate feedback structure with optional outcome tracking
    
    // Construct case object
    new_case = {
        "id": generate_uuid(),
        "query": state.query,
        "context": state.query_context,
        "agents_engaged": state.triggered_agents,
        "debate_transcript": compile_debate_transcript(state),
        "final_recommendation": final_recommendation,
        "timestamp": current_timestamp(),
        
        // Immediate feedback (captured right after delivery)
        "user_feedback": {
            "quality_score": None,  // To be filled by user
            "feedback_text": None,
            "submitted_at": None
        },
        
        // Long-term outcome (optional, updated when known)
        "outcome": {
            "status": "not_implemented",  // Initial state
            "alignment_score": None,
            "actual_results": None,
            "verified_at": None
        }
    }
    
    // Generate embedding for future retrieval
    case_embedding = generate_case_embedding(new_case)
    new_case.embedding = case_embedding
    
    // Store in vector database
    store_in_chroma({
        "collection": "historical_cases",
        "document": new_case,
        "embedding": case_embedding,
        "metadata": {
            "timestamp": new_case.timestamp,
            "agents_engaged": new_case.agents_engaged,
            "convergence_achieved": convergence_details.converged
        }
    })
    
    // Log storage
    LOG_INFO("Stored case " + new_case.id + " in memory system")
    
    RETURN new_case.id
END FUNCTION

FUNCTION update_case_outcome(case_id, outcome_data):
    // Updates a stored case with long-term outcome information
    // Called asynchronously when implementation results are known
    
    // Retrieve existing case
    existing_case = retrieve_case_by_id(case_id)
    
    IF existing_case IS NULL THEN
        LOG_ERROR("Case " + case_id + " not found for outcome update")
        RETURN False
    END IF
    
    // Update outcome fields
    existing_case.outcome = {
        "status": outcome_data.status,  // "implemented", "in_progress", "abandoned"
        "alignment_score": outcome_data.alignment_score,  // 1-5 scale
        "actual_results": outcome_data.actual_results,
        "verified_at": current_timestamp()
    }
    
    // Update in vector database
    update_in_chroma({
        "collection": "historical_cases",
        "document_id": case_id,
        "updated_fields": {
            "outcome": existing_case.outcome
        }
    })
    
    LOG_INFO("Updated case " + case_id + " with verified outcome")
    
    RETURN True
END FUNCTION

FUNCTION generate_case_embedding(case):
    // Generates embedding for case storage and retrieval
    // Combines query, context, and recommendation for comprehensive representation
    
    // Construct text for embedding
    embedding_text = ""
    embedding_text = embedding_text + "Query: " + case.query + "\n"
    embedding_text = embedding_text + "Context: " + stringify(case.context) + "\n"
    embedding_text = embedding_text + "Recommendation: " + case.final_recommendation.summary + "\n"
    embedding_text = embedding_text + "Agents: " + JOIN(case.agents_engaged, ", ")
    
    // Generate embedding using same model as query embeddings
    embedding = invoke_embedding_model(embedding_text)
    
    RETURN embedding
END FUNCTION
```

---

## 5. KNOWLEDGE ACCESS ROUTING LOGIC (Enhanced Hybrid C)

```
FUNCTION route_knowledge_access(query, static_retrieval_confidence):
    // Routes knowledge access across 3-tier architecture
    // Tier 1: Static vector DB (fast)
    // Tier 2: Dynamic web search (current info)
    // Tier 3: Agent system prompts (always active)
    // Returns {tier_used: str, knowledge: dict, metadata: dict}
    
    knowledge_result = {
        "tier_used": None,
        "knowledge": {},
        "metadata": {}
    }
    
    // Step 1: Check for date/recency keywords (Tier 2 trigger)
    date_keywords = ["latest", "current", "recent", "new", "today", "2024", "2025"]
    contains_date_keyword = check_for_keywords(query, date_keywords)
    
    // Step 2: Determine tier routing
    IF contains_date_keyword THEN
        // Trigger Tier 2 (dynamic) with Tier 1 (static) hybrid
        knowledge_result = use_hybrid_tier_1_and_2(query)
        knowledge_result.tier_used = "hybrid_1_2"
        knowledge_result.metadata.trigger_reason = "date_keyword_detected"
        
    ELSE IF static_retrieval_confidence < 0.7 THEN
        // Low confidence in static knowledge - use hybrid
        knowledge_result = use_hybrid_tier_1_and_2(query)
        knowledge_result.tier_used = "hybrid_1_2"
        knowledge_result.metadata.trigger_reason = "low_static_confidence"
        
    ELSE
        // High confidence in static knowledge - fast path (Tier 1 only)
        knowledge_result = use_tier_1_only(query)
        knowledge_result.tier_used = "tier_1_static"
        knowledge_result.metadata.trigger_reason = "high_static_confidence"
    END IF
    
    // Step 3: Tier 3 (agent system prompts) always active
    // Agent system prompts are loaded from YAML configs
    // This tier is implicit - agents always have their core principles
    
    RETURN knowledge_result
END FUNCTION

FUNCTION use_tier_1_only(query):
    // Retrieves knowledge from static vector database only
    // Fast path for stable regulatory information
    // Returns {knowledge: dict, confidence: float, sources: list}
    
    // Generate query embedding
    query_embedding = generate_query_embedding(query)
    
    // Search static knowledge base (Chroma)
    static_results = vector_search_chroma({
        "embedding": query_embedding,
        "collection": "eu_regulations",
        "top_k": 5,
        "similarity_threshold": 0.7
    })
    
    // Compile knowledge from results
    knowledge = {
        "retrieved_documents": [],
        "combined_confidence": 0
    }
    
    confidences = []
    FOR EACH result IN static_results:
        knowledge.retrieved_documents.ADD({
            "document": result.document,
            "source": result.metadata.source,
            "relevance": result.similarity_score,
            "chunk_text": result.text
        })
        confidences.ADD(result.similarity_score)
    END FOR
    
    // Calculate combined confidence
    IF LENGTH(confidences) > 0 THEN
        knowledge.combined_confidence = AVERAGE(confidences)
    ELSE
        knowledge.combined_confidence = 0
    END IF
    
    RETURN {
        "knowledge": knowledge,
        "confidence": knowledge.combined_confidence,
        "sources": extract_sources(static_results),
        "latency_ms": measure_latency(),  // Should be <500ms
        "tier": "static_only"
    }
END FUNCTION

FUNCTION use_hybrid_tier_1_and_2(query):
    // Combines static vector DB with dynamic web search
    // For queries requiring current information
    // Returns {knowledge: dict, confidence: float, sources: list, conflicts: list}
    
    // Retrieve from Tier 1 (static)
    static_knowledge = use_tier_1_only(query)
    
    // Retrieve from Tier 2 (dynamic web search)
    dynamic_knowledge = use_tier_2_dynamic(query)
    
    // Combine results with weighting (static 70%, dynamic 30%)
    combined_knowledge = {
        "static_contribution": static_knowledge.knowledge,
        "dynamic_contribution": dynamic_knowledge.knowledge,
        "combined_documents": []
    }
    
    // Weight static sources at 70%
    FOR EACH doc IN static_knowledge.knowledge.retrieved_documents:
        doc.weighted_relevance = doc.relevance * 0.7
        doc.source_type = "static_regulatory_db"
        combined_knowledge.combined_documents.ADD(doc)
    END FOR
    
    // Weight dynamic sources at 30%
    FOR EACH doc IN dynamic_knowledge.knowledge.retrieved_documents:
        doc.weighted_relevance = doc.relevance * 0.3
        doc.source_type = "dynamic_web_search"
        combined_knowledge.combined_documents.ADD(doc)
    END FOR
    
    // Sort by weighted relevance
    combined_knowledge.combined_documents = SORT(combined_knowledge.combined_documents BY weighted_relevance DESCENDING)
    
    // Detect conflicts between static and dynamic sources
    conflicts = detect_knowledge_conflicts(static_knowledge, dynamic_knowledge)
    
    // Calculate combined confidence
    combined_confidence = (static_knowledge.confidence * 0.7) + (dynamic_knowledge.confidence * 0.3)
    
    RETURN {
        "knowledge": combined_knowledge,
        "confidence": combined_confidence,
        "sources": combine_sources(static_knowledge.sources, dynamic_knowledge.sources),
        "conflicts": conflicts,
        "tier": "hybrid_static_dynamic"
    }
END FUNCTION

FUNCTION use_tier_2_dynamic(query):
    // Performs dynamic web search with sovereignty safeguards
    // Prioritizes EU-hosted sources
    // Returns {knowledge: dict, confidence: float, sources: list}
    
    // Define source priority order
    source_priority = [
        "EUR-Lex",  // EU official legal database (primary)
        "European Commission",  // EC websites (secondary)
        "General Web"  // Fallback (with sovereignty logging)
    ]
    
    dynamic_results = []
    
    // Priority 1: Search EUR-Lex
    eurlex_results = search_eurlex(query)
    IF LENGTH(eurlex_results) > 0 THEN
        FOR EACH result IN eurlex_results:
            result.priority = "primary_eu_source"
            result.sovereignty_flag = False
            dynamic_results.ADD(result)
        END FOR
    END IF
    
    // Priority 2: Search European Commission sites
    ec_results = search_european_commission(query)
    IF LENGTH(ec_results) > 0 THEN
        FOR EACH result IN ec_results:
            result.priority = "secondary_eu_source"
            result.sovereignty_flag = False
            dynamic_results.ADD(result)
        END FOR
    END IF
    
    // Priority 3: General web search (fallback with sovereignty logging)
    IF LENGTH(dynamic_results) < 3 THEN
        // Need more sources, use general web search
        web_results = search_general_web(query)
        
        FOR EACH result IN web_results:
            // Flag non-EU sources for audit
            IF NOT is_eu_hosted(result.domain) THEN
                result.sovereignty_flag = True
                LOG_SOVEREIGNTY_ACCESS(result.url, query)
            END IF
            
            result.priority = "fallback_external"
            dynamic_results.ADD(result)
        END FOR
    END IF
    
    // Compile knowledge
    knowledge = {
        "retrieved_documents": dynamic_results,
        "eu_sources_count": COUNT(dynamic_results WHERE sovereignty_flag == False),
        "external_sources_count": COUNT(dynamic_results WHERE sovereignty_flag == True)
    }
    
    // Calculate confidence based on source quality
    confidence_score = calculate_dynamic_confidence(dynamic_results)
    
    RETURN {
        "knowledge": knowledge,
        "confidence": confidence_score,
        "sources": extract_sources(dynamic_results),
        "sovereignty_flagged": knowledge.external_sources_count > 0,
        "tier": "dynamic_web_search"
    }
END FUNCTION

FUNCTION detect_knowledge_conflicts(static_knowledge, dynamic_knowledge):
    // Detects contradictions between static and dynamic sources
    // Returns list of conflicts with flagging for user notification
    
    conflicts = []
    
    // Extract factual claims from both sources
    static_claims = extract_factual_claims(static_knowledge)
    dynamic_claims = extract_factual_claims(dynamic_knowledge)
    
    // Check for contradictions
    FOR EACH static_claim IN static_claims:
        FOR EACH dynamic_claim IN dynamic_claims:
            IF are_contradictory(static_claim, dynamic_claim) THEN
                conflicts.ADD({
                    "static_claim": static_claim.text,
                    "static_source": static_claim.source,
                    "dynamic_claim": dynamic_claim.text,
                    "dynamic_source": dynamic_claim.source,
                    "conflict_type": "factual_contradiction",
                    "user_flag_message": "Static knowledge says '" + static_claim.text + "' but recent source says '" + dynamic_claim.text + "'. Verify current status."
                })
            END IF
        END FOR
    END FOR
    
    RETURN conflicts
END FUNCTION

FUNCTION calculate_dynamic_confidence(dynamic_results):
    // Calculates confidence score based on source quality and diversity
    // Returns float 0-1
    
    confidence = 0.5  // Base confidence
    
    // Boost for EU primary sources
    eu_primary_count = COUNT(dynamic_results WHERE priority == "primary_eu_source")
    confidence = confidence + (eu_primary_count * 0.15)  // +15% per EUR-Lex source
    
    // Boost for EU secondary sources
    eu_secondary_count = COUNT(dynamic_results WHERE priority == "secondary_eu_source")
    confidence = confidence + (eu_secondary_count * 0.10)  // +10% per EC source
    
    // Penalty for external sources only
    external_only = COUNT(dynamic_results WHERE sovereignty_flag == True) == LENGTH(dynamic_results)
    IF external_only THEN
        confidence = confidence - 0.2  // -20% if all sources are external
    END IF
    
    // Cap at 1.0
    IF confidence > 1.0 THEN
        confidence = 1.0
    END IF
    
    RETURN confidence
END FUNCTION

FUNCTION check_for_keywords(query, keyword_list):
    // Checks if query contains any keywords from list (case-insensitive)
    // Returns bool
    
    query_lowercase = TO_LOWERCASE(query)
    
    FOR EACH keyword IN keyword_list:
        keyword_lowercase = TO_LOWERCASE(keyword)
        IF CONTAINS(query_lowercase, keyword_lowercase) THEN
            RETURN True
        END IF
    END FOR
    
    RETURN False
END FUNCTION

FUNCTION LOG_SOVEREIGNTY_ACCESS(url, query):
    // Logs access to non-EU sources for audit compliance
    // Per sovereignty safeguards in gap resolutions
    
    audit_log_entry = {
        "timestamp": current_timestamp(),
        "event_type": "external_source_access",
        "url": url,
        "query": query,
        "domain": extract_domain(url),
        "is_eu_hosted": False,
        "reason": "Insufficient EU sources available"
    }
    
    APPEND_TO_AUDIT_LOG(audit_log_entry)
    
    RETURN
END FUNCTION
```

---

## APPENDIX: State Schema and Data Structures

### Core State Schema

```
STRUCTURE ConsortiumState:
    // Query and context
    query: string
    query_context: dict
    conversation_history: list[Message]
    
    // Agent engagement
    triggered_agents: list[string]
    agent_confidence_scores: dict[string, float]
    sub_questions: list[SubQuestion]
    assignments: dict[string, list[SubQuestion]]
    
    // Debate tracking
    agent_responses: dict[string, AgentResponse]
    iteration_counts: dict[tuple[string, string], int]
    current_proposal: Proposal
    
    // Memory and knowledge
    memory_retrievals: list[Case]
    knowledge_tier_used: string
    knowledge_conflicts: list[Conflict]
    
    // Convergence
    convergence_status: ConvergenceStatus
    convergence_details: dict
    
    // Tensions
    active_tensions: list[TensionProtocol]
    tension_iterations: dict[string, int]
    
    // Output
    final_recommendation: Report (optional)
    escalation_required: bool
    escalation_report: dict (optional)
    
    // Audit
    timestamp_start: datetime
    timestamp_end: datetime (optional)
    audit_trail: list[AuditEvent]
END STRUCTURE
```

### Agent Response Structure

```
STRUCTURE AgentResponse:
    agent_id: string
    rating: enum["BLOCK", "WARN", "ACCEPT", "ENDORSE"]
    confidence: float  // 0-1 scale
    reasoning: string
    attack_vector: string (optional)  // For adversarial critique
    evidence: list[string]  // Citations to knowledge sources
    
    // For WARN ratings
    mitigation_plan: string (optional)
    mitigation_accepted: bool (optional)
    rejection_reason: string (optional)
    
    timestamp: datetime
END STRUCTURE
```

### Case Structure (Memory System)

```
STRUCTURE Case:
    id: uuid
    query: string
    context: dict
    agents_engaged: list[string]
    debate_transcript: list[AgentResponse]
    final_recommendation: Report
    timestamp: datetime
    
    // Immediate feedback (Hybrid B component)
    user_feedback:
        quality_score: float  // 1-5 scale
        feedback_text: string (optional)
        submitted_at: datetime (optional)
    
    // Long-term outcome (Hybrid C component)
    outcome:
        status: enum["not_implemented", "in_progress", "implemented", "abandoned"]
        alignment_score: float (optional)  // 1-5 scale
        actual_results: string (optional)
        verified_at: datetime (optional)
    
    // Retrieval metadata
    embedding: vector
END STRUCTURE
```

### Convergence Status Structure

```
STRUCTURE ConvergenceStatus:
    converged: bool
    status: string
    details: dict
    failed_criteria: list[string]
    timestamp: datetime
END STRUCTURE
```

---

## Phase P Completion Checklist

- [x] 1. Supervisor Routing Algorithm
  - [x] Query analysis and keyword extraction
  - [x] Semantic similarity calculation
  - [x] Agent engagement decision (max 7 agents)
  - [x] Sub-question decomposition with MECE validation
  - [x] Always-engaged agents (Economist, Architect)

- [x] 2. All Five Tension Protocols
  - [x] Sovereign ↔ Economist (trust premium, 4 iterations)
  - [x] Eco-System ↔ Architect (SCI calculation, 3 iterations)
  - [x] Jurist ↔ Philosopher (instant escalation)
  - [x] Operator ↔ Strategy Agents (timeline revision, 2 iterations)
  - [x] Futurist ↔ All Agents (scenario robustness, 3 iterations)

- [x] 3. Convergence Testing Algorithm
  - [x] Zero BLOCK check
  - [x] WARN count ≤2 validation
  - [x] Mitigation acceptance verification
  - [x] Combined confidence >70% calculation
  - [x] 60% ACCEPT/ENDORSE threshold check

- [x] 4. Memory Retrieval Strategy (Hybrid B+C)
  - [x] Query embedding generation
  - [x] Vector search with quality filtering (≥3.5)
  - [x] Outcome-based weighting
  - [x] Cold-start handling
  - [x] Case storage with async outcome updates

- [x] 5. Knowledge Access Routing (Enhanced Hybrid C)
  - [x] Three-tier decision logic
  - [x] Date keyword detection
  - [x] Confidence threshold triggering (<0.7)
  - [x] Source prioritization (EUR-Lex → EC → Web)
  - [x] Static/dynamic combination (70/30 weighting)
  - [x] Conflict detection and flagging
  - [x] Sovereignty logging

---

## Next Step: Phase A (Architecture)

**Status**: âš ï¸ AWAITING APPROVAL

This pseudocode document defines all core algorithmic logic for the European Strategy Consortium. Upon approval, proceed to Phase A to define:

1. State schema implementation details
2. Graph topology and node structure
3. Component interfaces (Agent base class, Provider adapters)
4. Technology stack (Python 3.11+, LangGraph, Chroma, etc.)
5. Multi-LLM provider strategy
6. Testing approach and historical test cases

**STOP**: Please review and approve this pseudocode before proceeding to Phase A (Architecture).

---

**Document Status**: DRAFT  
**Methodology Compliance**: SPARC Phase P Complete  
**Awaiting**: Human approval to proceed to Phase A
