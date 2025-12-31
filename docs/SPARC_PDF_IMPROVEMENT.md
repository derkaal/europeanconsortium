# SPARC Design: PDF Report Structure Improvement

**Date:** 2025-12-31
**Objective:** Transform PDF output from unstructured agent outputs into a professional, board-grade report with executive summary, structured solutions, and detailed reasoning chapters.

---

## S - SPECIFICATION

### 1.1 Problem Statement

**Current State:**
- PDF contains raw agent responses concatenated together
- No executive summary or clear recommendation structure
- Reasoning scattered across 12 agent cards
- Difficult to extract actionable insights
- No enhanced research or solution enrichment

**Desired State:**
- Professional report structure:
  - **Executive Summary** (1-2 pages): Key findings, recommendation, critical actions
  - **Recommended Solutions** (2-3 pages): Structured solution design with implementation roadmap
  - **Detailed Analysis by Chapter** (8-12 pages):
    - Data Sovereignty & AI Sovereignty
    - Financial & Legal Analysis
    - Technical Architecture & Security
    - Sustainability & Ethics
    - Cultural & User Considerations
    - Strategic Opportunities (Alchemist/Founder insights)
  - **Appendices**: Raw agent outputs, tensions log, methodology

### 1.2 Requirements

**Functional Requirements:**
- FR1: Generate executive summary from synthesized recommendation
- FR2: Structure solutions with implementation phases and success criteria
- FR3: Organize agent reasoning into thematic chapters
- FR4: Enhance solutions with additional research and context
- FR5: Maintain all existing agent outputs (preserve for appendix)
- FR6: Zero impact on UI (changes only affect PDF generation)

**Non-Functional Requirements:**
- NFR1: Maintain zero-LLM cost for synthesis (use local processing where possible)
- NFR2: Optional LLM enhancement only for report writing agent
- NFR3: Execution time <5 seconds for report generation
- NFR4: Professional PDF formatting (matching board-grade standards)

### 1.3 Constraints

- UI must remain unchanged
- Existing agent structure must remain intact
- Graph flow should not require major refactoring
- PDF generation should be backward compatible (work with existing state structure)

---

## P - PSEUDOCODE

### 2.1 New Agent: `report_writer` (Report Structuring Agent)

```python
class ReportWriterAgent(Agent):
    """
    Transforms raw agent outputs into structured report sections.

    Responsibilities:
    - Generate executive summary from final_recommendation
    - Structure solutions into implementation phases
    - Organize agent reasoning into thematic chapters
    - Create chapter introductions and transitions
    """

    def invoke(state: ConsortiumState) -> AgentResponse:
        """
        Input:
            - agent_responses (all 12 agents)
            - final_recommendation
            - tensions
            - convergence_status

        Output:
            - structured_report: {
                "executive_summary": "...",
                "solution_overview": "...",
                "implementation_phases": [...],
                "chapters": [
                    {
                        "title": "Data & AI Sovereignty",
                        "content": "...",
                        "agents_referenced": ["sovereign", "intelligence_sovereign"]
                    },
                    ...
                ]
              }
        """

        # Step 1: Generate Executive Summary
        executive_summary = synthesize_executive_summary(
            recommendation=state.final_recommendation['recommendation'],
            convergence=state.convergence_status,
            critical_actions=filter_actions_by_priority('CRITICAL')
        )

        # Step 2: Structure Solutions
        solution_overview = create_solution_structure(
            recommendation=state.final_recommendation,
            agent_responses=state.agent_responses
        )

        implementation_phases = extract_implementation_phases(
            action_items=state.final_recommendation['action_items']
        )

        # Step 3: Organize into Chapters
        chapters = organize_into_chapters(
            agent_responses=state.agent_responses,
            chapter_mapping=CHAPTER_STRUCTURE
        )

        return {
            "executive_summary": executive_summary,
            "solution_overview": solution_overview,
            "implementation_phases": implementation_phases,
            "chapters": chapters
        }
```

**Chapter Organization Logic:**
```python
CHAPTER_STRUCTURE = {
    "1_sovereignty": {
        "title": "Data & AI Sovereignty",
        "agents": ["sovereign", "intelligence_sovereign"],
        "focus": "Jurisdictional control, vendor lock-in, strategic intel protection"
    },
    "2_financial_legal": {
        "title": "Financial & Legal Analysis",
        "agents": ["economist", "jurist"],
        "focus": "Cost-benefit, ROI, Feature Subsidy Doctrine, GDPR compliance"
    },
    "3_technical": {
        "title": "Technical Architecture & Security",
        "agents": ["architect", "technologist"],
        "focus": "Systems design, DR plans, encryption, SIEM integration"
    },
    "4_values": {
        "title": "Sustainability & Ethics",
        "agents": ["ecosystem", "philosopher"],
        "focus": "Carbon footprint, renewable energy, autonomy, dignity"
    },
    "5_cultural_user": {
        "title": "Cultural Fit & User Protection",
        "agents": ["ethnographer", "consumer_voice"],
        "focus": "Works councils, regional norms, privacy, transparency"
    },
    "6_strategic": {
        "title": "Strategic Opportunities & Value Creation",
        "agents": ["alchemist", "founder"],
        "focus": "Regulation-to-value transmutation, feature arbitrage"
    }
}
```

### 2.2 New Agent: `research_enhancer` (Solution Enhancement Agent)

```python
class ResearchEnhancerAgent(Agent):
    """
    Enhances recommended solutions with additional research and context.

    Responsibilities:
    - Add market context (competitor analysis, industry trends)
    - Provide case studies and precedents
    - Add technical references (standards, frameworks, tools)
    - Enrich with regulatory updates
    """

    def invoke(state: ConsortiumState) -> AgentResponse:
        """
        Input:
            - final_recommendation
            - agent_responses
            - context (industry, markets)

        Output:
            - enhanced_content: {
                "market_context": "...",
                "case_studies": [...],
                "technical_references": [...],
                "regulatory_landscape": "..."
              }
        """

        # Step 1: Extract key topics from recommendation
        key_topics = extract_topics(state.final_recommendation)

        # Step 2: Gather market context
        market_context = research_market_context(
            industry=state.context['industry'],
            topics=key_topics
        )

        # Step 3: Find relevant case studies
        case_studies = find_case_studies(
            agent_responses=state.agent_responses,
            memory_store=state.memory  # Leverage existing memory
        )

        # Step 4: Add technical references
        technical_references = gather_technical_references(
            agents_referenced=["architect", "technologist"],
            topics=key_topics
        )

        # Step 5: Regulatory landscape
        regulatory_landscape = compile_regulatory_info(
            agents_referenced=["jurist", "sovereign"],
            markets=state.context['markets']
        )

        return {
            "market_context": market_context,
            "case_studies": case_studies,
            "technical_references": technical_references,
            "regulatory_landscape": regulatory_landscape
        }
```

### 2.3 Graph Integration (Minimal Changes)

```python
# Add new node AFTER synthesizer, BEFORE PDF generation
# This happens at PDF generation time, NOT in main graph

def generate_consortium_pdf(query, context, agent_responses, tensions,
                           final_recommendation, convergence_status):
    """
    Enhanced PDF generation with report structuring.
    """

    # NEW: Invoke report structuring agents
    structured_report = invoke_report_writer(
        agent_responses=agent_responses,
        final_recommendation=final_recommendation,
        tensions=tensions,
        convergence_status=convergence_status
    )

    enhanced_content = invoke_research_enhancer(
        final_recommendation=final_recommendation,
        agent_responses=agent_responses,
        context=context
    )

    # Generate PDF with new structure
    pdf_buffer = create_structured_pdf(
        query=query,
        context=context,
        structured_report=structured_report,
        enhanced_content=enhanced_content,
        raw_outputs={  # Preserve for appendix
            "agent_responses": agent_responses,
            "tensions": tensions,
            "convergence_status": convergence_status
        }
    )

    return pdf_buffer
```

---

## A - ARCHITECTURE

### 3.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    EXISTING GRAPH FLOW                      │
│  (Scout → Router → Agent Executor → Tension Detector →     │
│   Tension Resolver → Convergence → CLA → Architect →       │
│   Advantage Analysis → SYNTHESIZER)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  Streamlit UI  │ ◄── No Changes
              │  (Display)     │
              └────────┬───────┘
                       │
                       │ User clicks "Download PDF"
                       ▼
┌──────────────────────────────────────────────────────────────┐
│              PDF GENERATION PIPELINE (ENHANCED)              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────┐           │
│  │ 1. REPORT WRITER AGENT                       │           │
│  ├──────────────────────────────────────────────┤           │
│  │  Input: agent_responses, final_recommendation│           │
│  │  Output: structured_report                   │           │
│  │    - executive_summary                       │           │
│  │    - solution_overview                       │           │
│  │    - implementation_phases                   │           │
│  │    - chapters (6 thematic sections)          │           │
│  └──────────────────┬───────────────────────────┘           │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────┐           │
│  │ 2. RESEARCH ENHANCER AGENT (Optional)        │           │
│  ├──────────────────────────────────────────────┤           │
│  │  Input: final_recommendation, context        │           │
│  │  Output: enhanced_content                    │           │
│  │    - market_context                          │           │
│  │    - case_studies                            │           │
│  │    - technical_references                    │           │
│  │    - regulatory_landscape                    │           │
│  └──────────────────┬───────────────────────────┘           │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────┐           │
│  │ 3. PDF RENDERER (ReportLab)                  │           │
│  ├──────────────────────────────────────────────┤           │
│  │  Section 1: Executive Summary (2 pages)      │           │
│  │  Section 2: Recommended Solutions (3 pages)  │           │
│  │  Section 3: Detailed Analysis (6 chapters)   │           │
│  │  Section 4: Implementation Roadmap (2 pages) │           │
│  │  Appendix A: Raw Agent Outputs               │           │
│  │  Appendix B: Tensions & Resolutions          │           │
│  │  Appendix C: Methodology & Convergence       │           │
│  └──────────────────┬───────────────────────────┘           │
│                     │                                        │
│                     ▼                                        │
│              PDF BytesIO Buffer                              │
│                     │                                        │
└─────────────────────┼────────────────────────────────────────┘
                      │
                      ▼
              Download to User
```

### 3.2 Data Flow Architecture

```
STATE AFTER SYNTHESIZER:
┌─────────────────────────────────────────┐
│ ConsortiumState                         │
├─────────────────────────────────────────┤
│ - query                                 │
│ - context                               │
│ - agent_responses (12 agents)           │
│ - tensions                              │
│ - final_recommendation                  │
│ - convergence_status                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ REPORT WRITER TRANSFORMATION             │
├──────────────────────────────────────────┤
│                                          │
│  Agent Responses → Chapters              │
│  ┌────────────────────────┐              │
│  │ sovereign              │ ──┐          │
│  │ intelligence_sovereign │ ──┼──► Ch1   │
│  ├────────────────────────┤   │          │
│  │ economist              │ ──┐          │
│  │ jurist                 │ ──┼──► Ch2   │
│  ├────────────────────────┤   │          │
│  │ architect              │ ──┐          │
│  │ technologist           │ ──┼──► Ch3   │
│  ├────────────────────────┤   │          │
│  │ ecosystem              │ ──┐          │
│  │ philosopher            │ ──┼──► Ch4   │
│  ├────────────────────────┤   │          │
│  │ ethnographer           │ ──┐          │
│  │ consumer_voice         │ ──┼──► Ch5   │
│  ├────────────────────────┤   │          │
│  │ alchemist              │ ──┐          │
│  │ founder                │ ──┼──► Ch6   │
│  └────────────────────────┘   │          │
│                                          │
│  Final Recommendation → Executive Summary│
│  Action Items → Implementation Phases    │
│                                          │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ RESEARCH ENHANCER ENRICHMENT             │
├──────────────────────────────────────────┤
│  Topics Extracted → Market Research      │
│  Memory Retrieved → Case Studies         │
│  Agent References → Technical Docs       │
│  Jurist/Sovereign → Regulatory Updates   │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ PDF DOCUMENT STRUCTURE                   │
├──────────────────────────────────────────┤
│ 1. Cover Page                            │
│ 2. Table of Contents (auto-generated)    │
│ 3. Executive Summary                     │
│ 4. Recommended Solutions                 │
│ 5. Implementation Roadmap                │
│ 6. Chapter 1: Sovereignty                │
│ 7. Chapter 2: Financial & Legal          │
│ 8. Chapter 3: Technical & Security       │
│ 9. Chapter 4: Values & Ethics            │
│ 10. Chapter 5: Cultural & User           │
│ 11. Chapter 6: Strategic Opportunities   │
│ 12. Appendix A: Raw Agent Outputs        │
│ 13. Appendix B: Tensions & Resolutions   │
│ 14. Appendix C: Methodology              │
└──────────────────────────────────────────┘
```

### 3.3 File Structure

```
europeanconsortium/
├── agents/
│   ├── base.py                      # Existing
│   ├── report_writer.py             # NEW: Report structuring agent
│   └── research_enhancer.py         # NEW: Solution enhancement agent
│
├── app/
│   ├── streamlit_app.py             # No changes (UI stays same)
│   ├── pdf_export.py                # REFACTOR: New PDF structure
│   └── pdf_components.py            # NEW: Reusable PDF components
│
├── src/consortium/
│   ├── nodes/
│   │   ├── synthesizer.py           # No changes
│   │   ├── report_structuring.py    # NEW: Report writer invocation
│   │   └── research_enhancement.py  # NEW: Research enhancer invocation
│   │
│   └── utils/
│       ├── chapter_organizer.py     # NEW: Chapter mapping logic
│       └── report_templates.py      # NEW: Report section templates
│
└── docs/
    ├── SPARC_PDF_IMPROVEMENT.md     # This document
    └── PDF_STRUCTURE_SPEC.md        # NEW: PDF template specification
```

---

## R - REFINEMENT

### 4.1 Implementation Strategy

**Phase 1: Foundation (Zero LLM Cost)**
1. Create `chapter_organizer.py` with deterministic chapter mapping
2. Create `report_templates.py` with section templates
3. Refactor `pdf_export.py` to use new structure
4. Test with existing data (no new agents yet)

**Phase 2: Report Writer Agent (Optional LLM)**
1. Implement `ReportWriterAgent` in `agents/report_writer.py`
2. Create prompt engineering for executive summary generation
3. Add chapter introduction/transition generation
4. Integrate into PDF generation pipeline

**Phase 3: Research Enhancement (Optional LLM)**
1. Implement `ResearchEnhancerAgent` in `agents/research_enhancer.py`
2. Add market context research capability
3. Integrate with existing memory store for case studies
4. Add to PDF as enrichment sections

**Phase 4: Polish & Optimization**
1. Add table of contents auto-generation
2. Implement cross-referencing between sections
3. Add visual elements (charts for convergence, tables for action items)
4. Performance optimization (caching, parallel execution)

### 4.2 LLM Cost Optimization Strategy

**Zero-LLM Baseline (Phase 1):**
- Executive summary: Template-based extraction from `final_recommendation`
- Chapter organization: Rule-based mapping using `CHAPTER_STRUCTURE`
- Implementation phases: Deterministic grouping by action priority

**Optional LLM Enhancement (Phases 2-3):**
- Report Writer: Use fast model (e.g., `mistral-small-latest`) for polish
- Research Enhancer: Use only if user enables (config flag)
- Estimated cost per report: <$0.10 with Mistral Small

**Configuration:**
```python
# config.yaml
pdf:
  enable_llm_report_writer: true  # Default: true (better reports)
  enable_research_enhancer: false  # Default: false (cost savings)
  report_writer_model: "mistral-small-latest"
  research_enhancer_model: "mistral-large-latest"
```

### 4.3 Report Writer Prompt Engineering

```python
REPORT_WRITER_SYSTEM_PROMPT = """
You are a professional report writer for European executive boards.

Your task is to transform technical agent analyses into clear, actionable
executive summaries and chapter introductions.

Guidelines:
- Use clear, jargon-free language suitable for C-suite executives
- Lead with key insights and recommendations
- Provide context before technical details
- Use European business conventions (e.g., €, GDPR references)
- Maintain professional, objective tone
- Structure content with clear headings and bullet points

You will receive:
1. Final recommendation from consortium
2. Agent responses (technical analyses)
3. Convergence status

You will produce:
1. Executive Summary (1-2 pages)
2. Chapter introductions (1 paragraph each)
3. Section transitions
"""

EXECUTIVE_SUMMARY_TEMPLATE = """
Generate a board-grade executive summary from the following:

RECOMMENDATION:
{final_recommendation}

CONVERGENCE STATUS:
{convergence_status}

CRITICAL ACTIONS:
{critical_actions}

STRUCTURE:
1. Opening: State the strategic question and recommendation (2-3 sentences)
2. Key Findings: 3-5 bullet points highlighting major insights
3. Critical Actions: Prioritized next steps with owners
4. Risk Assessment: Major concerns and mitigation strategies
5. Confidence Assessment: Convergence metrics and consensus level

Target length: 400-600 words
Tone: Professional, decisive, action-oriented
"""
```

### 4.4 Chapter Organization Algorithm

```python
def organize_into_chapters(agent_responses: dict,
                          chapter_mapping: dict) -> list:
    """
    Organize agent responses into thematic chapters.

    Algorithm:
    1. For each chapter in CHAPTER_STRUCTURE:
       a. Collect responses from designated agents
       b. Sort by rating severity (BLOCK > WARN > ACCEPT > ENDORSE)
       c. Generate chapter introduction (context for this theme)
       d. Combine agent reasonings with transitions
       e. Extract key insights and recommendations

    2. Add cross-references:
       - If sovereign references architect, add link
       - If economist references jurist, add link

    3. Format for PDF rendering
    """

    chapters = []

    for chapter_id, chapter_config in chapter_mapping.items():
        # Step 1: Collect relevant agent responses
        chapter_agents = {
            agent_id: agent_responses[agent_id]
            for agent_id in chapter_config['agents']
            if agent_id in agent_responses
        }

        # Step 2: Sort by severity
        sorted_agents = sorted(
            chapter_agents.items(),
            key=lambda x: RATING_SEVERITY[x[1]['rating']],
            reverse=True
        )

        # Step 3: Generate chapter introduction (LLM or template)
        intro = generate_chapter_intro(
            title=chapter_config['title'],
            focus=chapter_config['focus'],
            agents=sorted_agents
        )

        # Step 4: Combine agent content
        content_sections = []
        for agent_id, response in sorted_agents:
            section = format_agent_section(
                agent_id=agent_id,
                response=response,
                chapter_context=chapter_config['focus']
            )
            content_sections.append(section)

        # Step 5: Extract key insights
        key_insights = extract_key_insights(sorted_agents)

        chapters.append({
            'id': chapter_id,
            'title': chapter_config['title'],
            'introduction': intro,
            'sections': content_sections,
            'key_insights': key_insights,
            'agents_referenced': chapter_config['agents']
        })

    return chapters

RATING_SEVERITY = {
    'BLOCK': 4,
    'WARN': 3,
    'ACCEPT': 2,
    'ENDORSE': 1
}
```

### 4.5 PDF Section Templates

**Executive Summary Template:**
```
┌─────────────────────────────────────────────────────────────┐
│                      EXECUTIVE SUMMARY                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ STRATEGIC QUESTION:                                         │
│ {query}                                                     │
│                                                             │
│ RECOMMENDATION: {recommendation_statement}                  │
│                                                             │
│ CONFIDENCE LEVEL: {convergence_percentage}%                 │
│ CONSENSUS: {positive_percentage}% positive ratings          │
│                                                             │
│ ───────────────────────────────────────────────────────────│
│                                                             │
│ KEY FINDINGS:                                               │
│ • {finding_1}                                               │
│ • {finding_2}                                               │
│ • {finding_3}                                               │
│                                                             │
│ ───────────────────────────────────────────────────────────│
│                                                             │
│ CRITICAL ACTIONS (Immediate Attention Required):            │
│ 1. {critical_action_1} - Owner: {owner_1}                   │
│ 2. {critical_action_2} - Owner: {owner_2}                   │
│                                                             │
│ ───────────────────────────────────────────────────────────│
│                                                             │
│ RISK ASSESSMENT:                                            │
│ Major Concerns: {major_concerns_summary}                    │
│ Mitigation Strategy: {mitigation_summary}                   │
│                                                             │
│ ───────────────────────────────────────────────────────────│
│                                                             │
│ DECISION CONFIDENCE:                                        │
│ This recommendation achieved {iteration_count} round(s)     │
│ of consortium deliberation with {tensions_resolved}         │
│ tensions successfully resolved.                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Chapter Template:**
```
┌─────────────────────────────────────────────────────────────┐
│ CHAPTER {number}: {TITLE}                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ {chapter_introduction}                                      │
│                                                             │
│ ───────────────────────────────────────────────────────────│
│                                                             │
│ {AGENT_NAME_1} - {Rating} (Confidence: {conf}%)             │
│                                                             │
│ {reasoning_paragraph_1}                                     │
│                                                             │
│ {reasoning_paragraph_2}                                     │
│                                                             │
│ Key Concerns:                                               │
│ • {concern_1}                                               │
│ • {concern_2}                                               │
│                                                             │
│ Mitigation Plan: {mitigation}                               │
│                                                             │
│ ───────────────────────────────────────────────────────────│
│                                                             │
│ {AGENT_NAME_2} - {Rating} (Confidence: {conf}%)             │
│ ...                                                         │
│                                                             │
│ ───────────────────────────────────────────────────────────│
│                                                             │
│ KEY INSIGHTS FROM THIS CHAPTER:                             │
│ 1. {insight_1}                                              │
│ 2. {insight_2}                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## C - COMPLETION

### 5.1 Implementation Checklist

**Core Infrastructure:**
- [ ] Create `src/consortium/utils/chapter_organizer.py`
- [ ] Create `src/consortium/utils/report_templates.py`
- [ ] Create `app/pdf_components.py` (reusable PDF elements)

**Agent Implementation:**
- [ ] Create `agents/report_writer.py` (ReportWriterAgent class)
- [ ] Create `agents/research_enhancer.py` (ResearchEnhancerAgent class)
- [ ] Add agent configurations to `agents/` directory

**PDF Rendering:**
- [ ] Refactor `app/pdf_export.py` with new structure
- [ ] Implement executive summary section
- [ ] Implement solutions overview section
- [ ] Implement chapter sections (6 chapters)
- [ ] Implement implementation roadmap section
- [ ] Implement appendices (raw outputs, tensions, methodology)
- [ ] Add table of contents generation

**Integration:**
- [ ] Create `src/consortium/nodes/report_structuring.py`
- [ ] Create `src/consortium/nodes/research_enhancement.py`
- [ ] Update `app/streamlit_app.py` PDF button handler
- [ ] Add configuration options for LLM usage

**Testing:**
- [ ] Test with existing agent outputs (backward compatibility)
- [ ] Test chapter organization logic
- [ ] Test PDF rendering with new structure
- [ ] Test with LLM report writer enabled
- [ ] Test with research enhancer enabled
- [ ] Test cost optimization (compare LLM vs non-LLM)

**Documentation:**
- [ ] Create `docs/PDF_STRUCTURE_SPEC.md`
- [ ] Update README with new PDF features
- [ ] Add configuration documentation

### 5.2 Rollout Strategy

**Stage 1: Rule-Based Foundation (Zero LLM)**
- Deploy chapter organization logic
- Deploy new PDF structure
- Keep LLM agents disabled
- Validate improvement over current PDF

**Stage 2: Report Writer Agent (Optional LLM)**
- Enable report writer agent with toggle
- A/B test: LLM vs template-based executive summary
- Measure user satisfaction and cost

**Stage 3: Research Enhancement (Optional LLM)**
- Enable research enhancer with toggle
- Add market context and case studies
- Measure value-add vs cost

**Stage 4: Full Deployment**
- Make report writer default (with config override)
- Keep research enhancer opt-in
- Monitor costs and quality metrics

### 5.3 Success Metrics

**Quality Metrics:**
- Executive summary clarity (user survey)
- Chapter organization effectiveness (user survey)
- Actionability of implementation roadmap (user survey)

**Performance Metrics:**
- PDF generation time (<5 seconds target)
- LLM cost per report (<$0.10 target)
- Memory usage (should not increase significantly)

**User Adoption:**
- PDF download rate (vs current)
- User satisfaction score (vs current)
- Repeat usage rate

### 5.4 Risk Mitigation

**Risk 1: LLM Cost Explosion**
- Mitigation: Default to zero-LLM baseline, make enhancement opt-in
- Fallback: Template-based generation if LLM fails

**Risk 2: PDF Generation Time**
- Mitigation: Implement caching for report writer output
- Fallback: Show progress indicator in UI

**Risk 3: Backward Compatibility**
- Mitigation: Ensure new PDF generation works with old state format
- Fallback: Keep old `generate_consortium_pdf` as `generate_consortium_pdf_legacy`

**Risk 4: Report Quality Degradation**
- Mitigation: A/B testing before full rollout
- Fallback: User toggle to switch back to raw output PDF

---

## APPENDIX A: Configuration Schema

```yaml
# config/pdf_report_config.yaml

pdf_report:
  # Structure configuration
  enable_structured_report: true
  enable_table_of_contents: true
  enable_executive_summary: true
  enable_implementation_roadmap: true

  # Agent configuration
  enable_report_writer: true
  enable_research_enhancer: false  # Opt-in (cost consideration)

  # LLM configuration
  report_writer:
    model: "mistral-small-latest"
    temperature: 0.3
    max_tokens: 2000

  research_enhancer:
    model: "mistral-large-latest"
    temperature: 0.4
    max_tokens: 3000
    enable_market_research: true
    enable_case_studies: true
    enable_technical_references: true

  # PDF styling
  page_size: "A4"
  font_family: "Helvetica"
  heading_color: "#1a1a1a"
  accent_color: "#0066cc"

  # Chapter configuration
  chapters:
    - id: "sovereignty"
      title: "Data & AI Sovereignty"
      agents: ["sovereign", "intelligence_sovereign"]
      enabled: true

    - id: "financial_legal"
      title: "Financial & Legal Analysis"
      agents: ["economist", "jurist"]
      enabled: true

    - id: "technical"
      title: "Technical Architecture & Security"
      agents: ["architect", "technologist"]
      enabled: true

    - id: "values"
      title: "Sustainability & Ethics"
      agents: ["ecosystem", "philosopher"]
      enabled: true

    - id: "cultural_user"
      title: "Cultural Fit & User Protection"
      agents: ["ethnographer", "consumer_voice"]
      enabled: true

    - id: "strategic"
      title: "Strategic Opportunities"
      agents: ["alchemist", "founder"]
      enabled: true
```

---

## APPENDIX B: Example PDF Structure

**Page Distribution (Target: 25-30 pages)**

1. **Cover Page** (1 page)
2. **Table of Contents** (1 page)
3. **Executive Summary** (2 pages)
4. **Recommended Solutions** (3 pages)
   - Solution Overview
   - Implementation Phases
   - Success Criteria
5. **Implementation Roadmap** (2 pages)
   - Timeline (Critical → High → Medium → Low)
   - Resource Requirements
   - Risk Mitigation
6. **Chapter 1: Data & AI Sovereignty** (2-3 pages)
7. **Chapter 2: Financial & Legal Analysis** (2-3 pages)
8. **Chapter 3: Technical Architecture & Security** (2-3 pages)
9. **Chapter 4: Sustainability & Ethics** (2 pages)
10. **Chapter 5: Cultural Fit & User Protection** (2 pages)
11. **Chapter 6: Strategic Opportunities** (2-3 pages)
12. **Appendix A: Raw Agent Outputs** (3-4 pages)
13. **Appendix B: Tensions & Resolutions** (1-2 pages)
14. **Appendix C: Methodology & Convergence** (1 page)

---

## APPENDIX C: Implementation Priority

**High Priority (Must Have):**
1. Chapter organization logic (deterministic)
2. Executive summary template
3. Structured PDF rendering
4. Implementation roadmap section

**Medium Priority (Should Have):**
1. Report Writer Agent (LLM-enhanced)
2. Table of contents auto-generation
3. Cross-referencing between chapters
4. Visual elements (charts, tables)

**Low Priority (Nice to Have):**
1. Research Enhancer Agent
2. Market context sections
3. Case study enrichment
4. Advanced styling (colors, graphics)

---

**END OF SPARC DESIGN DOCUMENT**
