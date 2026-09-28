"""
Generate a professional, executive-ready PowerPoint presentation (.pptx)
for the MARINE-SHIELD project.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Initialize Presentation
prs = Presentation()
prs.slide_width = Inches(13.333)  # 16:9 widescreen layout
prs.slide_height = Inches(7.5)

# Color Palette: Ocean / Marine Theme
C_NAVY_DARK = RGBColor(10, 25, 47)      # #0A192F (Deep Navy)
C_NAVY_MID  = RGBColor(13, 59, 102)     # #0D3B66 (Ocean Depth)
C_BLUE_ACC  = RGBColor(0, 119, 182)     # #0077B6 (Ocean Blue)
C_TEAL      = RGBColor(0, 150, 136)     # #009688 (Marine Teal)
C_CYAN_ACC  = RGBColor(100, 255, 218)   # #64FFDA (Vibrant Aqua)
C_WHITE     = RGBColor(255, 255, 255)
C_LIGHT_BG  = RGBColor(248, 250, 252)   # #F8FAFC (Soft Slate)
C_CARD_BG   = RGBColor(255, 255, 255)
C_TEXT_DARK = RGBColor(15, 23, 42)      # #0F172A
C_TEXT_MUTED= RGBColor(74, 85, 104)     # #4A5568
C_RED_ACC   = RGBColor(220, 38, 38)     # #DC2626


def create_base_slide(title_text: str, category_text: str = "MARINE-SHIELD ARCHITECTURE"):
    """Create a standardized slide with dark marine header banner."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)

    # Background canvas
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_LIGHT_BG
    bg.line.fill.background()

    # Top Banner
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = C_NAVY_DARK
    header.line.fill.background()

    # Category Text
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.18), Inches(11.5), Inches(0.3))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = C_CYAN_ACC

    # Title Text
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.5), Inches(0.6))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE

    # Footer banner
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.7), Inches(0.35))
    tf_foot = footer_box.text_frame
    p_foot = tf_foot.paragraphs[0]
    p_foot.text = "MARINE-SHIELD: AI-Powered Marine Pollution Detection, Assessment & Response • Confidential & Proprietary"
    p_foot.font.size = Pt(9)
    p_foot.font.color.rgb = C_TEXT_MUTED

    return slide


def add_card(slide, left, top, width, height, title, body_bullets, accent_color=C_BLUE_ACC):
    """Add an elegant floating card with colored left accent and bullet points."""
    # Main card
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = C_CARD_BG
    card.line.color.rgb = RGBColor(226, 232, 240)
    card.line.width = Pt(1)

    # Left accent strip
    accent = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(0.12), height)
    accent.fill.solid()
    accent.fill.fore_color.rgb = accent_color
    accent.line.fill.background()

    # Content
    tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.15), width - Inches(0.35), height - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = C_TEXT_DARK
    p0.space_after = Pt(8)

    for item in body_bullets:
        p = tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(4)


# ========================================================
# SLIDE 1: Title Slide (Hero Dark Canvas)
# ========================================================
slide1 = prs.slides.add_slide(prs.slide_layouts[6])
bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
bg1.fill.solid()
bg1.fill.fore_color.rgb = C_NAVY_DARK
bg1.line.fill.background()

# Hero Header Box
tbox1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11), Inches(3.5))
tf1 = tbox1.text_frame
tf1.word_wrap = True

p_sub_pre = tf1.paragraphs[0]
p_sub_pre.text = "OCEANIC & COASTAL ENVIRONMENTAL INTELLIGENCE"
p_sub_pre.font.size = Pt(14)
p_sub_pre.font.bold = True
p_sub_pre.font.color.rgb = C_CYAN_ACC
p_sub_pre.space_after = Pt(10)

p_main = tf1.add_paragraph()
p_main.text = "MARINE-SHIELD"
p_main.font.size = Pt(44)
p_main.font.bold = True
p_main.font.color.rgb = C_WHITE
p_main.space_after = Pt(12)

p_desc = tf1.add_paragraph()
p_desc.text = "AI-Powered Marine Pollution Detection, Assessment & Grounded Response System"
p_desc.font.size = Pt(18)
p_desc.font.color.rgb = RGBColor(144, 224, 239)
p_desc.space_after = Pt(28)

p_meta = tf1.add_paragraph()
p_meta.text = "Computer Vision (MobileNetV3)  |  RAG (FAISS + MiniLM)  |  FastAPI & Streamlit  |  Automated PDF Reports"
p_meta.font.size = Pt(12)
p_meta.font.color.rgb = RGBColor(203, 213, 225)


# ========================================================
# SLIDE 2: The Global Challenge
# ========================================================
s2 = create_base_slide("The Marine Pollution Crisis & Operational Bottlenecks", "PROBLEM STATEMENT")
add_card(
    s2, Inches(0.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Ecological Threat",
    [
        "Over 14 million tons of plastic enter oceanic ecosystems annually.",
        "80% of marine debris accumulates in coastal intertidal zones.",
        "Microplastic fragmentation adsorbs persistent organic pollutants (POPs).",
        "Widespread mortality across sea turtles, cetaceans, and seabirds."
    ],
    C_RED_ACC
)
add_card(
    s2, Inches(4.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Ghost Gear Mortality",
    [
        "Abandoned, Lost, or Discarded Fishing Gear (ALDFG) continues 'ghost fishing'.",
        "Synthetic nylon nets remain lethal in benthic reefs for decades.",
        "Causes fatal entanglements and reef smothering.",
        "Severe physical hazard to divers, boat propellers, and volunteers."
    ],
    RGBColor(217, 119, 6)
)
add_card(
    s2, Inches(8.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Current Operational Gaps",
    [
        "Slow manual coastal surveys delay emergency interventions.",
        "Lack of standardized, explainable severity triage for field responders.",
        "Disconnected environmental manuals cause inconsistent PPE and segregation.",
        "No automated reporting pipeline for maritime and environmental authorities."
    ],
    C_BLUE_ACC
)


# ========================================================
# SLIDE 3: System Pipeline & Architecture
# ========================================================
s3 = create_base_slide("End-to-End Autonomous Pipeline Architecture", "SYSTEM ARCHITECTURE")
pipeline_steps = [
    ("1. Image Ingestion", ["Multipart image upload", "Format & corrupt validation", "Secure UUID persistence", "Edge & visual feature proxy"], C_BLUE_ACC),
    ("2. Deep Learning CV", ["MobileNetV3 transfer model", "6 pollution classes", "Confidence scoring", "Low-confidence triage flag"], C_TEAL),
    ("3. Severity Triage", ["Multi-factor rule matrix", "Base hazard weighting", "Edge density proxy", "Explainable rationale"], RGBColor(217, 119, 6)),
    ("4. RAG Intelligence", ["Sentence Transformers", "Persistent FAISS index", "6 Domain knowledge manuals", "Cosine similarity ranking"], RGBColor(99, 102, 241)),
    ("5. Grounded Output", ["5-section structured AI", "Strict anti-hallucination", "Offline synthesizer fallback", "Publication PDF report"], C_NAVY_MID)
]
for idx, (title, bullets, col) in enumerate(pipeline_steps):
    left = Inches(0.8 + idx * 2.4)
    add_card(s3, left, Inches(1.5), Inches(2.25), Inches(5.1), title, bullets, col)


# ========================================================
# SLIDE 4: Computer Vision Model
# ========================================================
s4 = create_base_slide("MobileNetV3 Classification & Verified Empirical Metrics", "COMPUTER VISION ENGINE")
add_card(
    s4, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.1),
    "Model Architecture & Training",
    [
        "Backbone: Pre-trained MobileNetV3-Small (lightweight & CPU-optimized).",
        "Custom Head: Linear(1024, 256) -> Hardswish -> Dropout(0.3) -> Linear(256, 6).",
        "Training Pipeline: AdamW optimizer, Cosine Annealing scheduler, data augmentation.",
        "6 Supported Classes:",
        "  1. Plastic Waste      4. Metal",
        "  2. Fishing Net        5. Organic Waste",
        "  3. Glass              6. Other Waste",
        "Confidence Safety: Auto-flags predictions below 0.60 threshold."
    ],
    C_TEAL
)
add_card(
    s4, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.1),
    "Empirical Test Performance (Verified)",
    [
        "Overall Test Accuracy: 87.5%",
        "Macro Precision: 92.86%  |  Macro Recall: 87.50%",
        "Macro F1-Score: 85.45%",
        "Class F1-Scores:",
        "  • Plastic Waste: 1.000 (100%)",
        "  • Fishing Net:   1.000 (100%)",
        "  • Glass:         1.000 (100%)",
        "  • Metal:         1.000 (100%)",
        "  • Other Waste:   0.727 (72.7%)",
        "  • Organic Waste: 0.400 (40.0%)",
        "Metrics stored permanently in models/evaluation_metrics.json."
    ],
    C_BLUE_ACC
)


# ========================================================
# SLIDE 5: Explainable Severity Assessment
# ========================================================
s5 = create_base_slide("Transparent Multi-Factor Severity Scoring", "SEVERITY ENGINE")
add_card(
    s5, Inches(0.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Base Hazard Weights",
    [
        "Inherent ecological threat weighting:",
        "• Fishing Net: 0.85 (Acute lethal ghost-fishing)",
        "• Plastic Waste: 0.70 (Microplastics & ingestion)",
        "• Metal: 0.65 (Oxidation & sharp hazard)",
        "• Glass: 0.50 (Laceration hazard)",
        "• Other Waste: 0.55 (Mixed debris)",
        "• Organic Waste: 0.35 (Biodegradable biomass)"
    ],
    RGBColor(217, 119, 6)
)
add_card(
    s5, Inches(4.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Visual Cues & Density",
    [
        "Computer Vision Feature Extraction:",
        "• Edge Density Filter: Measures debris boundary complexity and fragmentation.",
        "• Contrast & Clutter Score: Proxies multi-item accumulation vs isolated items.",
        "• Confidence Dampening: Low confidence automatically pulls extreme scores toward moderate triage."
    ],
    C_TEAL
)
add_card(
    s5, Inches(8.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Triage Output Levels",
    [
        "LOW Severity (< 0.40):",
        "  Isolated single-item debris; low immediate risk.",
        "MEDIUM Severity (0.40 - 0.70):",
        "  Moderate localized debris cluster.",
        "HIGH Severity (>= 0.70):",
        "  Dense accumulation or lethal entanglement net.",
        "Prominent Disclaimer: Prototype decision-support index, not a legal regulatory metric."
    ],
    C_NAVY_MID
)


# ========================================================
# SLIDE 6: RAG Semantic Retrieval
# ========================================================
s6 = create_base_slide("Retrieval-Augmented Generation (RAG) Architecture", "KNOWLEDGE ENGINE")
add_card(
    s6, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.1),
    "Semantic Retrieval Engine",
    [
        "Embedding Model: Sentence Transformers all-MiniLM-L6-v2 (384 dimensions).",
        "Vector Store: Persistent FAISS IndexFlatIP (exact Cosine Similarity).",
        "Persistence: Indexed once on disk (vectorstore/faiss_index.bin); sub-millisecond RAM search.",
        "Dynamic Query Formulation: Blends detected class, severity score, and user query.",
        "Output: Ranked source citations with document names, excerpts, and similarity scores."
    ],
    RGBColor(99, 102, 241)
)
add_card(
    s6, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.1),
    "Indexed Marine Manuals (24 Chunks)",
    [
        "1. KB-DOC-001: Marine Plastic Pollution & Microplastics",
        "   Degradation vectors, POPs adsorption, ingestion pathways.",
        "2. KB-DOC-002: Abandoned Fishing Gear (ALDFG)",
        "   Ghost net dynamics, entangled fauna rescue, specialized cutting.",
        "3. KB-DOC-003: Marine Glass & Metal Debris Hazards",
        "   Laceration triage, container pitfall traps, puncture-proof PPE.",
        "4. KB-DOC-004: Organic Coastal Waste & Algal Blooms",
        "   Sargassum eutrophication, anoxia, hydrogen sulfide emissions.",
        "5. KB-DOC-005: Coastal Cleanup Standard Operating Procedures",
        "   4-stream waste segregation, volunteer PPE, tidal timing.",
        "6. KB-DOC-006: 100-Meter Transect Environmental Monitoring",
        "   Debris density tallying, rapid triage scoring, evidence preservation."
    ],
    C_BLUE_ACC
)


# ========================================================
# SLIDE 7: Grounded AI Guidance & Guardrails
# ========================================================
s7 = create_base_slide("Factually Grounded AI Synthesis & Anti-Hallucination", "GENERATIVE AI & SAFETY")
add_card(
    s7, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.1),
    "Strict Anti-Hallucination Guardrails",
    [
        "Configurable LLM: Google Gemini 2.5 Flash, OpenAI, or local offline synthesizer.",
        "Strict System Instruction:",
        "  'Do not invent facts, statistics, regulations, laws, or scientific claims. Strictly ground responses on retrieved knowledge context.'",
        "Clear Separation of Tiers:",
        "  1. Computer Vision Prediction",
        "  2. Severity Assessment",
        "  3. Retrieved Factual Context",
        "  4. AI-Generated Recommendation",
        "Graceful Fallback: Deterministic offline synthesizer executes when API keys are absent."
    ],
    C_BLUE_ACC
)
add_card(
    s7, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.1),
    "Standardized 5-Section Environmental Report",
    [
        "Every assessment is structured into 5 standard sections:",
        "1. Detection Explanation:",
        "   Visual identification, material characteristics, confidence level.",
        "2. Environmental Significance:",
        "   Ingestion risks, chemical leachates, trophic web transfer.",
        "3. Recommended Response:",
        "   Actionable step-by-step cleanup protocol and PPE requirements.",
        "4. Monitoring Considerations:",
        "   Biofouling observations, GPS coordinates, transect density.",
        "5. Limitations:",
        "   Transparent AI prototype disclaimer and field verification notice."
    ],
    C_TEAL
)


# ========================================================
# SLIDE 8: Technology Stack & Full-Stack Implementation
# ========================================================
s8 = create_base_slide("Production-Grade Full-Stack Technology Stack", "IMPLEMENTATION DETAILS")
add_card(
    s8, Inches(0.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Backend & Services",
    [
        "• FastAPI & Uvicorn: High-throughput asynchronous REST API.",
        "• Pydantic v2: Strict request/response validation schema.",
        "• SQLAlchemy ORM & SQLite: Persistent storage for analyses, sources, and reports.",
        "• Interactive Swagger Documentation: Available at /docs.",
        "• Automated Lifecycle: Caches model and FAISS vector index on startup."
    ],
    C_NAVY_MID
)
add_card(
    s8, Inches(4.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Frontend & Reporting",
    [
        "• Streamlit 1.38+: Clean ocean-themed dashboard with 7 navigation modules.",
        "• Interactive Cards: Real-time progress, severity badges, confidence meters.",
        "• ReportLab Platypus Engine: Generates multi-page publication-grade PDF incident reports.",
        "• Numbered Canvas: Dynamic page counting ('Page X of Y') and security footer.",
        "• Embedded Evidence: Includes uploaded thumbnail and RAG citation table."
    ],
    C_BLUE_ACC
)
add_card(
    s8, Inches(8.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Quality Assurance & DevOps",
    [
        "• Pytest Suite: 24 comprehensive tests covering all pipelines (100% pass rate in 22s).",
        "• Multi-Stage Dockerfile: Headless Linux container with libgl1 and dependencies.",
        "• Docker Compose: Isolated backend (8000) and frontend (8501) network services.",
        "• One-Click Windows Launcher: run.bat and run_app.py for instant local startup."
    ],
    C_TEAL
)


# ========================================================
# SLIDE 9: Deployment & Access Channels
# ========================================================
s9 = create_base_slide("Deployment Architecture & Access Channels", "DEPLOYMENT STRATEGY")
add_card(
    s9, Inches(0.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Streamlit Community Cloud",
    [
        "• 100% Free Public Cloud Hosting.",
        "• Linked to GitHub: vinola-J/MARINE-SHIELD.",
        "• Automatic CI/CD deployment on git push.",
        "• Built-in HTTPS SSL certificate.",
        "• Custom public URL: https://<app-name>.streamlit.app.",
        "• Environment secrets management for LLM keys."
    ],
    C_BLUE_ACC
)
add_card(
    s9, Inches(4.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Containerized Cloud (Docker)",
    [
        "• Multi-service docker-compose.yml configuration.",
        "• Compatible with AWS ECS, Google Cloud Run, Azure Container Apps, or Render.",
        "• Persistent volume mounts for database, reports, and models.",
        "• Automated healthcheck probes targeting /api/health."
    ],
    C_TEAL
)
add_card(
    s9, Inches(8.8), Inches(1.5), Inches(3.6), Inches(5.1),
    "Local & Edge Deployment",
    [
        "• One-click Windows batch launcher: run.bat.",
        "• Unified multi-server runner: run_app.py.",
        "• Localhost ports: 8501 (Frontend) & 8000 (Backend).",
        "• Low RAM/CPU Footprint: MobileNetV3 runs smoothly on standard laptop hardware without GPU."
    ],
    C_NAVY_MID
)


# ========================================================
# SLIDE 10: Environmental Impact & Future Roadmap
# ========================================================
s10 = create_base_slide("Environmental Impact, Roadmap & Next Steps", "FUTURE ROADMAP")
add_card(
    s10, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.1),
    "Immediate Environmental Value",
    [
        "• Rapid Triage: Shrinks coastal incident categorization from days to under 2 seconds.",
        "• Standardized Protocol: Prevents volunteer injuries through automated PPE and segregation guidance.",
        "• Scientific Evidence: Structured PDF reports bridge citizen science observations with municipal authorities.",
        "• Ghost Net Alert: High-severity escalation for derelict gear saves entangled marine wildlife."
    ],
    C_TEAL
)
add_card(
    s10, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.1),
    "Future Technological Roadmap",
    [
        "• Drone & UAV Stream Integration: Real-time aerial beach sweep video classification.",
        "• Semantic Segmentation (YOLOv11-Seg): Bounding box pixel-level debris volume estimation.",
        "• Direct Maritime API Feeds: Automated incident dispatch to NOAA and local marine sanctuary authorities.",
        "• Offline Edge Kit: Packaging for lightweight Raspberry Pi / NVIDIA Jetson field camera stations."
    ],
    C_BLUE_ACC
)

# Save presentation
output_path = Path("MARINE_SHIELD_Presentation.pptx")
prs.save(str(output_path))
print(f"Presentation saved successfully to: {output_path.resolve()}")
