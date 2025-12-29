"""
PDF Export Module for European Strategy Consortium

Generates professional PDF reports of consortium analysis results.
"""

from datetime import datetime
from io import BytesIO
from typing import Dict, Any, List

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak,
        Table, TableStyle
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def generate_consortium_pdf(
    query: str,
    context: Dict[str, Any],
    agent_responses: Dict[str, Any],
    tensions: List[Dict[str, Any]],
    final_recommendation: Dict[str, Any],
    convergence_status: Dict[str, Any]
) -> BytesIO:
    """
    Generate PDF report of consortium analysis.
    
    Args:
        query: Strategic query
        context: Query context (industry, company size, etc.)
        agent_responses: Dict of agent responses
        tensions: List of detected tensions
        final_recommendation: Final recommendation dict
        convergence_status: Convergence status dict
    
    Returns:
        BytesIO buffer containing PDF
    """
    if not PDF_AVAILABLE:
        raise ImportError(
            "reportlab not installed. "
            "Install with: pip install reportlab"
        )
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for PDF elements
    story = []
    
    # Define styles
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
    story.append(Paragraph(
        "Strategic Analysis Report",
        subheading_style
    ))
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
            context_text.append(
                f"<b>Company Size:</b> {context['company_size']}"
            )
        if context.get('markets'):
            markets = ', '.join(context['markets'])
            context_text.append(f"<b>Target Markets:</b> {markets}")
        if context.get('constraints'):
            context_text.append(
                f"<b>Constraints:</b> {context['constraints']}"
            )
        
        for text in context_text:
            story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Agent responses section
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
            f"<b>Rating:</b> {rating} | "
            f"<b>Confidence:</b> {confidence:.0%}",
            body_style
        ))
        story.append(Paragraph(f"<b>Reasoning:</b> {reasoning}", body_style))
        
        if response.get('mitigation_plan'):
            story.append(Paragraph(
                f"<b>Mitigation:</b> {response['mitigation_plan']}",
                body_style
            ))
        
        story.append(Spacer(1, 0.15*inch))
    
    # Tensions section
    if tensions:
        story.append(PageBreak())
        story.append(Paragraph("Tensions Detected & Resolved", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        for tension in tensions:
            agents = tension.get('agents', 'Unknown')
            description = tension.get('description', 'N/A')
            resolution = tension.get('resolution', 'N/A')
            
            story.append(Paragraph(f"<b>{agents}</b>", subheading_style))
            story.append(Paragraph(
                f"<b>Conflict:</b> {description}",
                body_style
            ))
            story.append(Paragraph(
                f"<b>Resolution:</b> {resolution}",
                body_style
            ))
            story.append(Paragraph("<b>Status:</b> ✅ Resolved", body_style))
            story.append(Spacer(1, 0.15*inch))
    
    # Final recommendation section
    story.append(PageBreak())
    story.append(Paragraph("Final Recommendation", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Convergence status
    if convergence_status:
        converged = convergence_status.get('converged', False)
        status_text = "CONVERGED" if converged else "ESCALATED TO HUMAN"
        story.append(Paragraph(f"<b>Status:</b> {status_text}", body_style))
        
        if 'positive_percentage' in convergence_status:
            consensus = convergence_status['positive_percentage']
            story.append(Paragraph(
                f"<b>Consensus:</b> {consensus:.0f}%",
                body_style
            ))
        story.append(Spacer(1, 0.1*inch))
    
    # Recommendation text
    if isinstance(final_recommendation, dict):
        rec_text = final_recommendation.get('recommendation', 'N/A')
        story.append(Paragraph(rec_text, body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Action items ("Yes, If" conditions)
        if final_recommendation.get('action_items'):
            story.append(Paragraph('"Yes, If" Conditions', subheading_style))
            story.append(Spacer(1, 0.1*inch))
            
            for item in final_recommendation['action_items']:
                priority = item.get('priority', 'MEDIUM')
                action = item.get('action', 'N/A')
                owner = item.get('owner', 'N/A')
                details = item.get('details', '')
                
                priority_emoji = {
                    "HIGH": "🔴",
                    "MEDIUM": "🟡",
                    "LOW": "🟢",
                    "Critical": "🔴"
                }.get(priority, "⚪")
                
                story.append(Paragraph(
                    f"{priority_emoji} <b>{action}</b> ({owner})",
                    body_style
                ))
                if details:
                    story.append(Paragraph(f"<i>{details}</i>", body_style))
                story.append(Spacer(1, 0.1*inch))
    else:
        story.append(Paragraph(str(final_recommendation), body_style))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        "European Strategy Consortium • 10 Agents + CLA Meta-Agent • "
        '"Yes, If" Protocol',
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
