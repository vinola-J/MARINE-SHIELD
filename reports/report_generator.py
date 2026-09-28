import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    PageBreak
)
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "generated_reports"


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically display 'Page X of Y' and footer disclaimer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header rule
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, letter[1] - 40, letter[0] - 40, letter[1] - 40)
        self.drawString(40, letter[1] - 35, "MARINE-SHIELD: AI-Powered Marine Pollution Assessment & Response")

        # Footer rule
        self.line(40, 45, letter[0] - 40, 45)
        self.drawString(40, 32, "Confidential & Prototype Marine Triage — Not an official environmental assessment.")
        self.drawRightString(letter[0] - 40, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def generate_pollution_pdf_report(
    analysis_data: Dict[str, Any],
    output_filename: Optional[str] = None
) -> str:
    """
    Generate a structured, professional PDF report for a completed pollution analysis.
    
    Returns:
        Absolute filepath to the generated PDF.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    analysis_id = analysis_data.get("id", f"analysis_{int(datetime.now().timestamp())}")
    
    if not output_filename:
        output_filename = f"marine_shield_report_{analysis_id}.pdf"
    
    pdf_path = REPORTS_DIR / output_filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=55,
        bottomMargin=55
    )

    # Styling Palette
    c_primary = colors.HexColor("#0A192F")      # Deep Navy
    c_secondary = colors.HexColor("#0077B6")    # Ocean Blue
    c_teal = colors.HexColor("#009688")         # Marine Teal
    c_dark = colors.HexColor("#1A202C")         # Charcoal Text
    c_muted = colors.HexColor("#4A5568")        # Slate Grey
    c_light_bg = colors.HexColor("#F8FAFC")     # Soft Background

    # Severity accent colors
    sev = str(analysis_data.get("severity", "MEDIUM")).upper()
    if sev == "HIGH":
        sev_color = colors.HexColor("#DC2626")
    elif sev == "MEDIUM":
        sev_color = colors.HexColor("#D97706")
    else:
        sev_color = colors.HexColor("#16A34A")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_primary
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=c_secondary
    )

    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_dark
    )

    badge_style = ParagraphStyle(
        "BadgeText",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=sev_color
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#7F1D1D")
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("MARINE-SHIELD", title_style))
    elements.append(Paragraph("MARINE POLLUTION ASSESSMENT REPORT", subtitle_style))
    elements.append(Spacer(1, 10))

    # Meta Table
    timestamp_str = analysis_data.get("timestamp") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    meta_table_data = [
        [
            Paragraph(f"<b>Assessment ID:</b> {analysis_id}", body_style),
            Paragraph(f"<b>Date/Time:</b> {timestamp_str}", body_style)
        ],
        [
            Paragraph(f"<b>Status:</b> {analysis_data.get('status', 'COMPLETED')}", body_style),
            Paragraph(f"<b>Evaluation Engine:</b> Marine-Shield v1.0", body_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[260, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 12))

    # SECTION 1: AI MODEL PREDICTION (Clearly Demarcated)
    elements.append(Paragraph("1. COMPUTER VISION DETECTION RESULT", h1_style))
    
    # Check if image thumbnail exists
    img_element = Paragraph("<i>[No Image Attached]</i>", body_style)
    raw_img_path = analysis_data.get("image_path")
    if raw_img_path and Path(raw_img_path).exists():
        try:
            img_element = RLImage(str(raw_img_path), width=2.4*inch, height=1.8*inch)
        except Exception:
            img_element = Paragraph("<i>[Image Preview Unavailable]</i>", body_style)

    pred = analysis_data.get("prediction", "Unknown Waste")
    conf = float(analysis_data.get("confidence", 0.0)) * 100.0
    score = float(analysis_data.get("severity_score", 0.0))
    reason = analysis_data.get("severity_reason", "No reason provided.")

    findings_data = [
        [Paragraph("<b>Pollution Classification:</b>", body_style), Paragraph(f"<b>{pred}</b>", body_style)],
        [Paragraph("<b>Model Confidence:</b>", body_style), Paragraph(f"<b>{conf:.1f}%</b>", body_style)],
        [Paragraph("<b>Severity Triage Level:</b>", body_style), Paragraph(f"<b>{sev}</b> (Score: {score:.2f})", badge_style)],
        [Paragraph("<b>Severity Rationale:</b>", body_style), Paragraph(reason, body_style)]
    ]
    findings_table = Table(findings_data, colWidths=[130, 230])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor("#F1F5F9")),
    ]))

    cv_box_data = [
        [img_element, findings_table]
    ]
    cv_box = Table(cv_box_data, colWidths=[170, 360])
    cv_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light_bg),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(cv_box)
    elements.append(Spacer(1, 12))

    # SECTION 2: GROUNDED AI ASSESSMENT
    elements.append(Paragraph("2. GROUNDED AI ENVIRONMENTAL ASSESSMENT", h1_style))
    ai_text = analysis_data.get("ai_assessment", "No AI assessment recorded.")
    # Format markdown headers into clean paragraphs
    for line in ai_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("### "):
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(f"<b>{line.replace('### ', '')}</b>", ParagraphStyle(
                "SubH2", parent=body_style, fontName="Helvetica-Bold", fontSize=9.5, textColor=c_secondary
            )))
        elif line.startswith("- "):
            elements.append(Paragraph(f"• {line[2:]}", body_style))
        else:
            elements.append(Paragraph(line, body_style))
    elements.append(Spacer(1, 10))

    # SECTION 3: KNOWLEDGE-BASED RECOMMENDED RESPONSE
    elements.append(Paragraph("3. RECOMMENDED FIELD RESPONSE PROTOCOL", h1_style))
    rec_text = analysis_data.get("recommendation", "Follow standard shoreline survey protocols.")
    rec_box_data = [[
        Paragraph(rec_text.replace("\n", "<br/>"), body_style)
    ]]
    rec_box = Table(rec_box_data, colWidths=[530])
    rec_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(rec_box)
    elements.append(Spacer(1, 12))

    # SECTION 4: KNOWLEDGE SOURCES USED
    elements.append(Paragraph("4. KNOWLEDGE SOURCES RETRIEVED (RAG)", h1_style))
    sources: List[Dict[str, Any]] = analysis_data.get("sources", [])
    if sources:
        src_table_data = [
            [
                Paragraph("<b>Document / Reference</b>", table_header_style),
                Paragraph("<b>Category</b>", table_header_style),
                Paragraph("<b>Similarity</b>", table_header_style)
            ]
        ]
        for s in sources:
            name = s.get("document_name") or s.get("title") or "Marine Reference"
            cat = s.get("category", "Marine Pollution Guidance")
            sim = f"{float(s.get('similarity_score', 0.0)):.3f}"
            src_table_data.append([
                Paragraph(name, table_cell_style),
                Paragraph(cat, table_cell_style),
                Paragraph(sim, table_cell_style)
            ])
        src_table = Table(src_table_data, colWidths=[290, 170, 70])
        src_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_secondary),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light_bg])
        ]))
        elements.append(src_table)
    else:
        elements.append(Paragraph("<i>No external RAG knowledge sources were associated with this analysis.</i>", body_style))
    elements.append(Spacer(1, 14))

    # SECTION 5: OFFICIAL DISCLAIMER & LIMITATIONS
    disclaimer_text = (
        "<b>SYSTEM NOTICE & PROTOTYPE DISCLAIMER:</b><br/>"
        "This assessment report is generated automatically by the MARINE-SHIELD AI system (Computer Vision + "
        "Retrieval-Augmented Generation). It serves as a rapid triage and guidance tool. It is <b>NOT</b> a "
        "scientifically validated regulatory environmental severity index, nor does it constitute an official legal "
        "or governmental environmental citation. All recommendations must be confirmed on-site by qualified marine conservation "
        "authorities and trained emergency responders before initiating hazardous materials handling or salvage operations."
    )
    disclaimer_box = Table([[Paragraph(disclaimer_text, disclaimer_style)]], colWidths=[530])
    disclaimer_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#FCA5A5")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(KeepTogether(disclaimer_box))

    # Build PDF with dynamic 2-pass NumberedCanvas
    doc.build(elements, canvasmaker=NumberedCanvas)
    return str(pdf_path)
