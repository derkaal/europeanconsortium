"""
PDF Export Module for European Strategy Consortium

Generates professional, board-grade PDF reports with structured sections:
- Executive Summary
- Recommended Solutions
- Implementation Roadmap
- Thematic Chapters
- Appendices
"""

from datetime import datetime
from io import BytesIO
from typing import Dict, Any, List, Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Spacer, PageBreak
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Import our custom utilities
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.consortium.utils.chapter_organizer import (
        organize_into_chapters,
        format_agent_section,
        AGENT_DISPLAY_NAMES
    )
    from src.consortium.utils.report_templates import (
        generate_executive_summary,
        generate_solution_overview,
        generate_implementation_roadmap,
        generate_methodology_appendix
    )
    from app.pdf_components import (
        create_custom_styles,
        build_cover_page,
        build_section_header,
        build_chapter_header,
        build_subsection_header,
        build_body_text,
        build_bullet_list,
        build_rating_badge,
        build_action_items_table,
        build_convergence_metrics_table,
        build_divider,
        build_table_of_contents,
        MARGIN
    )
    UTILITIES_AVAILABLE = True
except ImportError as e:
    UTILITIES_AVAILABLE = False
    print(f"Warning: Could not import utilities: {e}")


def generate_consortium_pdf(
    query: str,
    context: Dict[str, Any],
    agent_responses: Dict[str, Any],
    tensions: List[Dict[str, Any]],
    final_recommendation: Dict[str, Any],
    convergence_status: Dict[str, Any],
    research_briefing: Optional[Dict[str, Any]] = None
) -> BytesIO:
    """
    Generate structured PDF report of consortium analysis.

    Args:
        query: Strategic query
        context: Query context (industry, company size, etc.)
        agent_responses: Dict of agent responses
        tensions: List of detected tensions
        final_recommendation: Final recommendation dict
        convergence_status: Convergence status dict
        research_briefing: Scout research briefing with external sources

    Returns:
        BytesIO buffer containing PDF
    """
    if not PDF_AVAILABLE:
        raise ImportError(
            "reportlab not installed. "
            "Install with: pip install reportlab"
        )

    if not UTILITIES_AVAILABLE:
        # Fallback to legacy PDF generation
        return generate_legacy_pdf(
            query, context, agent_responses, tensions,
            final_recommendation, convergence_status, research_briefing
        )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN
    )

    # Container for PDF elements
    story = []

    # Create custom styles
    styles = create_custom_styles()

    # Extract action items for processing
    action_items = final_recommendation.get('action_items', [])
    critical_actions = [a for a in action_items if a.get('priority') == 'CRITICAL']

    # ===== COVER PAGE =====
    cover_elements = build_cover_page(
        title="European Consortium Strategic Analysis",
        subtitle=query[:100] + "..." if len(query) > 100 else query,
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        styles=styles
    )
    story.extend(cover_elements)

    # ===== TABLE OF CONTENTS =====
    chapters = organize_into_chapters(agent_responses)
    toc_elements = build_table_of_contents(chapters, styles)
    story.extend(toc_elements)

    # ===== EXECUTIVE SUMMARY =====
    story.append(build_section_header("Executive Summary", styles))
    story.append(Spacer(1, 0.2))

    exec_summary = generate_executive_summary(
        query=query,
        final_recommendation=final_recommendation,
        convergence_status=convergence_status,
        critical_actions=critical_actions
    )

    # Split into paragraphs and render
    for paragraph in exec_summary.split('\n\n'):
        if paragraph.strip():
            # Check if it's a heading (all caps or ends with colon)
            if paragraph.strip().isupper() or paragraph.strip().endswith(':'):
                story.append(build_subsection_header(paragraph.strip(), styles))
            else:
                story.append(build_body_text(paragraph.strip(), styles))

    story.append(build_divider(styles))

    # Add convergence metrics table
    story.append(build_subsection_header("Decision Metrics", styles))
    story.append(build_convergence_metrics_table(convergence_status, styles))
    story.append(PageBreak())

    # ===== RECOMMENDED SOLUTIONS =====
    story.append(build_section_header("Recommended Solutions", styles))
    story.append(Spacer(1, 0.2))

    solution_overview = generate_solution_overview(
        final_recommendation=final_recommendation,
        agent_responses=agent_responses
    )

    for paragraph in solution_overview.split('\n\n'):
        if paragraph.strip():
            if paragraph.strip().isupper() or paragraph.strip().endswith(':'):
                story.append(build_subsection_header(paragraph.strip(), styles))
            else:
                # Check if it's a bullet list
                if paragraph.strip().startswith('•'):
                    items = [line.strip()[2:] for line in paragraph.split('\n')
                            if line.strip().startswith('•')]
                    story.extend(build_bullet_list(items, styles))
                else:
                    story.append(build_body_text(paragraph.strip(), styles))

    story.append(PageBreak())

    # ===== IMPLEMENTATION ROADMAP =====
    story.append(build_section_header("Implementation Roadmap", styles))
    story.append(Spacer(1, 0.2))

    roadmap = generate_implementation_roadmap(action_items)

    # Parse roadmap sections
    current_phase = None
    for line in roadmap.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Phase headers
        if line.startswith('PHASE'):
            story.append(build_subsection_header(line, styles))
        elif line.startswith('These ') or line.startswith('Address '):
            story.append(build_body_text(line, styles))
        elif line[0].isdigit() and '. ' in line:
            # Action item - extract number
            story.append(build_body_text(line, styles))
        elif line.startswith('Responsible:') or line.startswith('Details:'):
            story.append(build_body_text(f"   {line}", styles))

    story.append(build_divider(styles))

    # Add action items tables by priority
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        table = build_action_items_table(action_items, priority, styles)
        if table:
            story.append(build_subsection_header(f"{priority} Priority Actions", styles))
            story.append(table)
            story.append(Spacer(1, 0.2))

    story.append(PageBreak())

    # ===== THEMATIC CHAPTERS =====
    for chapter in chapters:
        chapter_num = chapter.get('number', 0)
        chapter_title = chapter.get('title', '')
        chapter_intro = chapter.get('introduction', '')
        chapter_agents = chapter.get('agents', [])
        key_insights = chapter.get('key_insights', [])

        # Chapter header
        story.append(build_chapter_header(chapter_num, chapter_title, styles))
        story.append(Spacer(1, 0.2))

        # Chapter introduction
        for paragraph in chapter_intro.split('\n\n'):
            if paragraph.strip():
                if paragraph.strip().startswith('•'):
                    items = [line.strip()[2:] for line in paragraph.split('\n')
                            if line.strip().startswith('•')]
                    story.extend(build_bullet_list(items, styles))
                else:
                    story.append(build_body_text(paragraph.strip(), styles))

        story.append(build_divider(styles))

        # Agent sections
        for agent_id, response in chapter_agents:
            agent_name = AGENT_DISPLAY_NAMES.get(agent_id, agent_id)
            rating = response.get('rating', 'ACCEPT')
            confidence = response.get('confidence', 0.0)
            reasoning = response.get('reasoning', '')
            attack_vector = response.get('attack_vector', '')
            mitigation_plan = response.get('mitigation_plan', '')

            # Agent header with rating badge
            story.extend(build_rating_badge(agent_name, rating, confidence, styles))

            # Reasoning
            story.append(build_body_text(reasoning, styles))

            # Attack vector (if present)
            if attack_vector:
                story.append(build_subsection_header("Key Concern:", styles))
                story.append(build_body_text(attack_vector, styles))

            # Mitigation plan (if present)
            if mitigation_plan:
                story.append(build_subsection_header("Mitigation Strategy:", styles))
                story.append(build_body_text(mitigation_plan, styles))

            story.append(build_divider(styles))

        # Key insights
        if key_insights:
            story.append(build_subsection_header("Key Insights from this Chapter:", styles))
            story.extend(build_bullet_list(key_insights, styles))
            story.append(Spacer(1, 0.2))

        story.append(PageBreak())

    # ===== APPENDIX A: AGENT ANALYSIS DETAILS =====
    story.append(build_section_header("Appendix A: Agent Analysis Details", styles))
    story.append(Spacer(1, 0.2))

    story.append(build_body_text(
        "This appendix contains the complete agent analysis outputs in the order "
        "they were presented during deliberation.",
        styles
    ))
    story.append(Spacer(1, 0.2))

    # List all agent responses with full details
    for agent_id, response in agent_responses.items():
        agent_name = AGENT_DISPLAY_NAMES.get(agent_id, agent_id)
        rating = response.get('rating', 'ACCEPT')
        confidence = response.get('confidence', 0.0)
        reasoning = response.get('reasoning', '')
        attack_vector = response.get('attack_vector', '')
        mitigation_plan = response.get('mitigation_plan', '')

        # Agent header with rating badge
        story.extend(build_rating_badge(agent_name, rating, confidence, styles))

        # Reasoning
        if reasoning:
            story.append(build_body_text(reasoning, styles, compact=True))

        # Attack vector (if present)
        if attack_vector:
            story.append(build_body_text("Key Concern:", styles, compact=True))
            story.append(build_body_text(attack_vector, styles, compact=True))

        # Mitigation plan (if present)
        if mitigation_plan:
            story.append(build_body_text("Mitigation Strategy:", styles, compact=True))
            story.append(build_body_text(mitigation_plan, styles, compact=True))

        story.append(Spacer(1, 0.15))

    story.append(PageBreak())

    # ===== APPENDIX B: TENSIONS & RESOLUTIONS =====
    story.append(build_section_header("Appendix B: Tensions & Resolutions", styles))
    story.append(Spacer(1, 0.2))

    if tensions:
        story.append(build_body_text(
            f"The consortium detected and resolved {len(tensions)} inter-agent tension(s) "
            "during deliberation. These tensions represent areas where agents had conflicting "
            "perspectives that required resolution.",
            styles
        ))
        story.append(Spacer(1, 0.2))

        for i, tension in enumerate(tensions, 1):
            agents = tension.get('agents', 'Unknown')
            description = tension.get('description', 'N/A')
            resolution = tension.get('resolution', 'N/A')

            story.append(build_subsection_header(f"Tension {i}: {agents}", styles))
            story.append(build_body_text(f"Conflict: {description}", styles, compact=True))
            story.append(build_body_text(f"Resolution: {resolution}", styles, compact=True))
            story.append(build_body_text("Status: ✅ Resolved", styles, compact=True))
            story.append(Spacer(1, 0.15))
    else:
        story.append(build_body_text(
            "No inter-agent tensions were detected during deliberation. "
            "This indicates strong alignment among the consortium agents.",
            styles
        ))

    story.append(PageBreak())

    # ===== APPENDIX C: EXTERNAL SOURCES =====
    if research_briefing:
        story.append(build_section_header("Appendix C: External Sources", styles))
        story.append(Spacer(1, 0.2))

        story.append(build_body_text(
            "This appendix lists the external sources consulted by The Scout agent during "
            "the initial research phase and during report compilation.",
            styles
        ))
        story.append(Spacer(1, 0.2))

        # Extract sources from research briefing
        exec_summary = research_briefing.get('executive_summary', '')
        searches_executed = research_briefing.get('searches_executed', 0)

        if exec_summary:
            story.append(build_subsection_header("Research Summary:", styles))
            story.append(build_body_text(exec_summary, styles))
            story.append(Spacer(1, 0.2))

        # Show agent briefings with sources
        agent_briefings = research_briefing.get('agent_briefings', {})
        if agent_briefings:
            story.append(build_subsection_header("Sources by Agent Domain:", styles))
            story.append(Spacer(1, 0.1))

            from src.consortium.utils.chapter_organizer import AGENT_DISPLAY_NAMES

            for agent_id, briefing in agent_briefings.items():
                agent_name = AGENT_DISPLAY_NAMES.get(agent_id, agent_id)
                sources = briefing.get('sources', [])

                if sources:
                    story.append(build_body_text(f"• {agent_name}:", styles, compact=True))
                    for source in sources:
                        story.append(build_body_text(f"  - {source}", styles, compact=True))
                    story.append(Spacer(1, 0.05))

        # Show total searches executed
        story.append(Spacer(1, 0.2))
        story.append(build_body_text(
            f"Total external searches executed: {searches_executed}",
            styles
        ))

        story.append(PageBreak())

    # ===== APPENDIX D: METHODOLOGY =====
    decision_provenance = final_recommendation.get('decision_provenance', {})
    methodology = generate_methodology_appendix(convergence_status, decision_provenance)

    for paragraph in methodology.split('\n\n'):
        if paragraph.strip():
            if paragraph.strip().isupper():
                story.append(build_section_header(paragraph.strip(), styles))
            elif paragraph.strip().endswith(':') and len(paragraph.strip()) < 100:
                story.append(build_subsection_header(paragraph.strip(), styles))
            else:
                # Check for bullet lists
                if '•' in paragraph:
                    items = [line.strip()[2:] for line in paragraph.split('\n')
                            if line.strip().startswith('•')]
                    story.extend(build_bullet_list(items, styles))
                else:
                    story.append(build_body_text(paragraph.strip(), styles))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_legacy_pdf(
    query: str,
    context: Dict[str, Any],
    agent_responses: Dict[str, Any],
    tensions: List[Dict[str, Any]],
    final_recommendation: Dict[str, Any],
    convergence_status: Dict[str, Any],
    research_briefing: Optional[Dict[str, Any]] = None
) -> BytesIO:
    """
    Legacy PDF generation (fallback if utilities not available).

    This is the original implementation preserved for backward compatibility.
    Note: research_briefing parameter is accepted but not used in legacy mode.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003399'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#003399'),
        spaceAfter=12,
        spaceBefore=12
    )

    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )

    # Title page
    story.append(Paragraph("🇪🇺 European Strategy Consortium", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Strategic Analysis Report", subheading_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        body_style
    ))
    story.append(Spacer(1, 0.5*inch))

    # Query section
    story.append(Paragraph("Strategic Query", heading_style))
    story.append(Paragraph(query, body_style))
    story.append(Spacer(1, 0.2*inch))

    # Context section
    if context:
        story.append(Paragraph("Context", heading_style))
        context_text = []
        if context.get('industry'):
            context_text.append(f"<b>Industry:</b> {context['industry']}")
        if context.get('company_size'):
            context_text.append(f"<b>Company Size:</b> {context['company_size']}")
        if context.get('markets'):
            markets = ', '.join(context['markets'])
            context_text.append(f"<b>Target Markets:</b> {markets}")
        if context.get('constraints'):
            context_text.append(f"<b>Constraints:</b> {context['constraints']}")

        for text in context_text:
            story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 0.2*inch))

    # Agent responses
    story.append(PageBreak())
    story.append(Paragraph("Agent Deliberation", heading_style))
    story.append(Spacer(1, 0.1*inch))

    agent_names = {
        "sovereign": "🛡️ Sovereign (Data Sovereignty)",
        "intelligence_sovereign": "🤖 Intelligence Sovereign (AI Sovereignty)",
        "economist": "💰 Economist (Financial Viability)",
        "jurist": "⚖️ Jurist (Legal Compliance)",
        "architect": "🏗️ Architect (Systems Design)",
        "ecosystem": "🌱 Eco-System (Sustainability)",
        "philosopher": "🧠 Philosopher (Ethics)",
        "ethnographer": "🌍 Ethnographer (Cultural Fit)",
        "technologist": "🔒 Technologist (Security)",
        "consumer_voice": "👥 Consumer Voice (User Protection)"
    }

    for agent_id, response in agent_responses.items():
        agent_name = agent_names.get(agent_id, agent_id)
        story.append(Paragraph(agent_name, subheading_style))

        rating = response.get('rating', 'N/A')
        confidence = response.get('confidence', 0)
        reasoning = response.get('reasoning', 'No reasoning provided')

        story.append(Paragraph(
            f"<b>Rating:</b> {rating} | <b>Confidence:</b> {confidence:.0%}",
            body_style
        ))
        story.append(Paragraph(f"<b>Reasoning:</b> {reasoning}", body_style))

        if response.get('mitigation_plan'):
            story.append(Paragraph(
                f"<b>Mitigation:</b> {response['mitigation_plan']}",
                body_style
            ))

        story.append(Spacer(1, 0.15*inch))

    # Tensions
    if tensions:
        story.append(PageBreak())
        story.append(Paragraph("Tensions Detected & Resolved", heading_style))
        story.append(Spacer(1, 0.1*inch))

        for tension in tensions:
            agents = tension.get('agents', 'Unknown')
            description = tension.get('description', 'N/A')
            resolution = tension.get('resolution', 'N/A')

            story.append(Paragraph(f"<b>{agents}</b>", subheading_style))
            story.append(Paragraph(f"<b>Conflict:</b> {description}", body_style))
            story.append(Paragraph(f"<b>Resolution:</b> {resolution}", body_style))
            story.append(Paragraph("<b>Status:</b> ✅ Resolved", body_style))
            story.append(Spacer(1, 0.15*inch))

    # Final recommendation
    story.append(PageBreak())
    story.append(Paragraph("Final Recommendation", heading_style))
    story.append(Spacer(1, 0.1*inch))

    if convergence_status:
        converged = convergence_status.get('converged', False)
        status_text = "CONVERGED" if converged else "ESCALATED TO HUMAN"
        story.append(Paragraph(f"<b>Status:</b> {status_text}", body_style))

        if 'positive_percentage' in convergence_status:
            consensus = convergence_status['positive_percentage']
            story.append(Paragraph(f"<b>Consensus:</b> {consensus:.0f}%", body_style))
        story.append(Spacer(1, 0.1*inch))

    if isinstance(final_recommendation, dict):
        rec_text = final_recommendation.get('recommendation', 'N/A')
        story.append(Paragraph(rec_text, body_style))
    else:
        story.append(Paragraph(str(final_recommendation), body_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
