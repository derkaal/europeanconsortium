"""
PDF Components Module

Provides reusable PDF rendering components for structured reports.
Uses ReportLab for professional document formatting.
"""

from io import BytesIO
from typing import List, Dict, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)


# PDF Styling Constants
PAGE_WIDTH = A4[0]
PAGE_HEIGHT = A4[1]
MARGIN = 0.75 * inch


def create_custom_styles():
    """
    Create custom paragraph styles for the report.

    Returns:
        Dictionary of custom styles
    """
    styles = getSampleStyleSheet()

    # Title style (cover page)
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    # Subtitle style
    styles.add(ParagraphStyle(
        name='CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))

    # Section heading (H1)
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderPadding=5,
        borderColor=colors.HexColor('#0066cc'),
        borderWidth=0,
        leftIndent=0
    ))

    # Chapter heading (H2)
    styles.add(ParagraphStyle(
        name='ChapterHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=10,
        spaceBefore=16,
        fontName='Helvetica-Bold'
    ))

    # Subsection heading (H3)
    styles.add(ParagraphStyle(
        name='SubsectionHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    ))

    # Body text (custom to avoid conflict with base stylesheet)
    styles.add(ParagraphStyle(
        name='CustomBodyText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=14
    ))

    # Body text compact (for appendices)
    styles.add(ParagraphStyle(
        name='BodyTextCompact',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=4,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=12
    ))

    # Bullet list item
    styles.add(ParagraphStyle(
        name='BulletItem',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=4,
        leftIndent=20,
        bulletIndent=10,
        fontName='Helvetica'
    ))

    # Agent rating badge style
    styles.add(ParagraphStyle(
        name='RatingBadge',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        spaceAfter=6
    ))

    # Metadata/footer style
    styles.add(ParagraphStyle(
        name='Metadata',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))

    # Warning box style
    styles.add(ParagraphStyle(
        name='WarningBox',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#cc6600'),
        fontName='Helvetica-Bold',
        leftIndent=15,
        rightIndent=15,
        spaceAfter=10,
        spaceBefore=10
    ))

    # Critical box style
    styles.add(ParagraphStyle(
        name='CriticalBox',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#cc0000'),
        fontName='Helvetica-Bold',
        leftIndent=15,
        rightIndent=15,
        spaceAfter=10,
        spaceBefore=10
    ))

    return styles


def build_cover_page(title: str, subtitle: str, date: str, styles: Dict) -> List:
    """
    Build cover page elements.

    Args:
        title: Report title
        subtitle: Report subtitle
        date: Generation date
        styles: Style dictionary

    Returns:
        List of PDF flowables
    """
    elements = []

    # Spacer to center content
    elements.append(Spacer(1, 2 * inch))

    # Title
    elements.append(Paragraph(title, styles['CustomTitle']))
    elements.append(Spacer(1, 0.3 * inch))

    # Subtitle
    elements.append(Paragraph(subtitle, styles['CustomSubtitle']))
    elements.append(Spacer(1, 1.5 * inch))

    # European Consortium branding
    branding = "European Consortium Multi-Agent Deliberation System"
    elements.append(Paragraph(branding, styles['CustomSubtitle']))
    elements.append(Spacer(1, 0.5 * inch))

    # Date
    elements.append(Paragraph(f"Generated: {date}", styles['Metadata']))

    # Page break after cover
    elements.append(PageBreak())

    return elements


def build_section_header(title: str, styles: Dict) -> Paragraph:
    """
    Build a section header.

    Args:
        title: Section title
        styles: Style dictionary

    Returns:
        Paragraph element
    """
    return Paragraph(title, styles['SectionHeading'])


def build_chapter_header(number: int, title: str, styles: Dict) -> Paragraph:
    """
    Build a chapter header.

    Args:
        number: Chapter number
        title: Chapter title
        styles: Style dictionary

    Returns:
        Paragraph element
    """
    header_text = f"Chapter {number}: {title}"
    return Paragraph(header_text, styles['ChapterHeading'])


def build_subsection_header(title: str, styles: Dict) -> Paragraph:
    """
    Build a subsection header.

    Args:
        title: Subsection title
        styles: Style dictionary

    Returns:
        Paragraph element
    """
    return Paragraph(title, styles['SubsectionHeading'])


def build_body_text(text: str, styles: Dict, compact: bool = False) -> Paragraph:
    """
    Build body text paragraph.

    Args:
        text: Text content
        styles: Style dictionary
        compact: Use compact formatting

    Returns:
        Paragraph element
    """
    style = styles['BodyTextCompact'] if compact else styles['CustomBodyText']

    # Escape special characters and preserve formatting
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    return Paragraph(text, style)


def build_bullet_list(items: List[str], styles: Dict) -> List:
    """
    Build a bullet list.

    Args:
        items: List of bullet items
        styles: Style dictionary

    Returns:
        List of paragraph elements
    """
    elements = []
    for item in items:
        # Escape special characters
        item = item.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        bullet_text = f"• {item}"
        elements.append(Paragraph(bullet_text, styles['BulletItem']))
    return elements


def build_rating_badge(agent_name: str, rating: str, confidence: float,
                       styles: Dict) -> List:
    """
    Build agent rating badge with color coding.

    Args:
        agent_name: Agent display name
        rating: Rating value (BLOCK, WARN, ACCEPT, ENDORSE)
        confidence: Confidence value (0-1)
        styles: Style dictionary

    Returns:
        List of flowable elements
    """
    elements = []

    # Color coding for ratings
    rating_colors = {
        'BLOCK': colors.HexColor('#cc0000'),
        'WARN': colors.HexColor('#ff9900'),
        'ACCEPT': colors.HexColor('#5cb85c'),
        'ENDORSE': colors.HexColor('#0066cc')
    }

    color = rating_colors.get(rating, colors.black)

    # Create badge text
    badge_text = f"<font color='#{color.hexval()[2:]}'><b>{agent_name}</b> - {rating} (Confidence: {confidence:.0%})</font>"

    elements.append(Paragraph(badge_text, styles['RatingBadge']))

    return elements


def build_action_items_table(action_items: List[Dict[str, Any]],
                             priority: str, styles: Dict) -> Optional[Table]:
    """
    Build action items table for a specific priority.

    Args:
        action_items: List of action items
        priority: Priority level to filter (CRITICAL, HIGH, MEDIUM, LOW)
        styles: Style dictionary

    Returns:
        Table element or None if no items
    """
    # Filter items by priority
    filtered_items = [item for item in action_items
                     if item.get('priority') == priority]

    if not filtered_items:
        return None

    # Build table data
    table_data = [['#', 'Action', 'Owner']]

    for i, item in enumerate(filtered_items, 1):
        action = item.get('action', 'No action specified')
        owner = item.get('owner', 'Not assigned')

        # Wrap text in paragraphs for better formatting
        action_para = Paragraph(action, styles['BodyTextCompact'])
        owner_para = Paragraph(owner, styles['BodyTextCompact'])

        table_data.append([str(i), action_para, owner_para])

    # Create table
    table = Table(table_data, colWidths=[0.5*inch, 4*inch, 2*inch])

    # Style the table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Number column centered
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
    ]))

    return table


def build_convergence_metrics_table(convergence_status: Dict[str, Any],
                                    styles: Dict) -> Table:
    """
    Build convergence metrics summary table.

    Args:
        convergence_status: Convergence status data
        styles: Style dictionary

    Returns:
        Table element
    """
    converged = convergence_status.get('converged', False)
    positive_percentage = convergence_status.get('positive_percentage', 0)
    iteration_count = convergence_status.get('iteration_count', 1)
    gate_status = convergence_status.get('gate_status', {})

    block_count = gate_status.get('block_count', 0)
    warn_count = gate_status.get('warn_count', 0)

    # Build table data
    table_data = [
        ['Metric', 'Value', 'Status'],
        ['Convergence Status', 'CONVERGED' if converged else 'ESCALATED', '✓' if converged else '✗'],
        ['Consensus Level', f"{positive_percentage}%", '✓' if positive_percentage >= 60 else '✗'],
        ['Iteration Count', str(iteration_count), '✓' if iteration_count <= 3 else '⚠'],
        ['Blocking Concerns', str(block_count), '✓' if block_count == 0 else '✗'],
        ['Warnings', str(warn_count), '✓' if warn_count <= 2 else '⚠']
    ]

    # Create table
    table = Table(table_data, colWidths=[2.5*inch, 2*inch, 1*inch])

    # Style the table
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),

        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
    ]))

    return table


def build_divider(styles: Dict) -> Spacer:
    """
    Build a visual divider between sections.

    Args:
        styles: Style dictionary

    Returns:
        Spacer element
    """
    return Spacer(1, 0.2 * inch)


def build_warning_box(text: str, styles: Dict) -> List:
    """
    Build a warning box for important notices.

    Args:
        text: Warning text
        styles: Style dictionary

    Returns:
        List of flowable elements
    """
    elements = []

    # Warning icon and text
    warning_text = f"⚠ WARNING: {text}"
    elements.append(Paragraph(warning_text, styles['WarningBox']))

    return elements


def build_critical_box(text: str, styles: Dict) -> List:
    """
    Build a critical/blocking concern box.

    Args:
        text: Critical concern text
        styles: Style dictionary

    Returns:
        List of flowable elements
    """
    elements = []

    # Critical icon and text
    critical_text = f"🚫 CRITICAL: {text}"
    elements.append(Paragraph(critical_text, styles['CriticalBox']))

    return elements


def build_table_of_contents(chapters: List[Dict[str, Any]], styles: Dict) -> List:
    """
    Build table of contents.

    Args:
        chapters: List of chapter dictionaries
        styles: Style dictionary

    Returns:
        List of flowable elements
    """
    elements = []

    elements.append(build_section_header("Table of Contents", styles))
    elements.append(Spacer(1, 0.2 * inch))

    # Main sections
    toc_items = [
        "Executive Summary",
        "Recommended Solutions",
        "Implementation Roadmap"
    ]

    # Add chapters
    for chapter in chapters:
        number = chapter.get('number', 0)
        title = chapter.get('title', '')
        toc_items.append(f"Chapter {number}: {title}")

    # Appendices
    toc_items.extend([
        "Appendix A: Agent Analysis Details",
        "Appendix B: Tensions & Resolutions",
        "Appendix C: External Sources",
        "Appendix D: Methodology"
    ])

    # Build TOC list
    elements.extend(build_bullet_list(toc_items, styles))

    elements.append(PageBreak())

    return elements


def build_footer(page_num: int, total_pages: int) -> str:
    """
    Build footer text.

    Args:
        page_num: Current page number
        total_pages: Total number of pages

    Returns:
        Footer text
    """
    return f"European Consortium Report | Page {page_num} of {total_pages}"
