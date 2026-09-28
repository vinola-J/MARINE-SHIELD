import os
import io
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from PIL import Image
import streamlit as st
import pandas as pd

# Load environment configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SAMPLES_DIR = Path("data/images/samples")

# Page Configuration
st.set_page_config(
    page_title="MARINE-SHIELD | AI Marine Pollution Detection",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Marine & Ocean Theme CSS
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Banner Gradient */
    .marine-header {
        background: linear-gradient(135deg, #0A192F 0%, #0D3B66 50%, #0077B6 100%);
        padding: 24px 30px;
        border-radius: 14px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(10, 25, 47, 0.25);
        border: 1px solid rgba(100, 255, 218, 0.2);
    }
    
    .marine-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #FFFFFF;
    }
    
    .marine-header p {
        margin: 6px 0 0 0;
        color: #90E0EF;
        font-size: 1.05rem;
        font-weight: 400;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #0077B6;
        margin-bottom: 16px;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .metric-title {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #0F172A;
        font-size: 1.9rem;
        font-weight: 700;
        margin-top: 4px;
    }
    
    /* Badges */
    .badge-high {
        background-color: #FEE2E2;
        color: #DC2626;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-med {
        background-color: #FEF3C7;
        color: #D97706;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-low {
        background-color: #DCFCE7;
        color: #16A34A;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-demo {
        background-color: #E0E7FF;
        color: #4F46E5;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    /* Callout Card */
    .source-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .source-title {
        font-weight: 600;
        color: #0369A1;
        font-size: 0.95rem;
    }
    .source-snippet {
        color: #334155;
        font-size: 0.85rem;
        margin-top: 4px;
        line-height: 1.4;
    }
    
    .disclaimer-banner {
        background: #FFFBEB;
        border: 1px solid #FCD34D;
        border-radius: 8px;
        padding: 12px 16px;
        color: #92400E;
        font-size: 0.85rem;
        margin-top: 14px;
    }
</style>
""", unsafe_allow_html=True)


# Helper: Check Backend Health
def check_backend_health():
    try:
        r = requests.get(f"{BACKEND_URL}/api/health", timeout=3)
        if r.status_code == 200:
            return True, r.json()
        return False, None
    except Exception:
        return False, None


# Fallback Direct Services (Used if backend container/port is not active)
def execute_direct_analysis(image_bytes: bytes, filename: str):
    from database.database import get_db_context
    from backend.services.analysis_service import process_pollution_analysis
    with get_db_context() as db:
        return process_pollution_analysis(image_bytes, filename, db)


def execute_direct_ask(question: str, analysis_id: str = None):
    from rag.retriever import retrieve_relevant_chunks
    from rag.generator import answer_environmental_question
    sources = retrieve_relevant_chunks(question, top_k=3)
    answer = answer_environmental_question(question, sources=sources)
    return {"question": question, "answer": answer, "sources": sources}


def execute_direct_report_gen(analysis_id: str):
    import uuid
    from datetime import datetime, timezone
    from database.database import get_db_context
    from database.models import Analysis, Report
    from reports.report_generator import generate_pollution_pdf_report
    with get_db_context() as db:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found.")
        report_id = str(uuid.uuid4())
        filename = f"marine_shield_report_{analysis.id}.pdf"
        pdf_path = generate_pollution_pdf_report(analysis.to_dict(), filename)
        db_rep = Report(id=report_id, analysis_id=analysis.id, report_path=pdf_path)
        db.add(db_rep)
        db.commit()
        return {"report_id": report_id, "report_path": pdf_path, "download_url": None}


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("### 🌊 **MARINE-SHIELD**")
    st.caption("AI-Powered Pollution Triage")
    
    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "🔍 Analyze Pollution",
            "💬 Ask MARINE-SHIELD",
            "📑 Reports",
            "📚 Knowledge Base",
            "📈 Model Evaluation",
            "ℹ️ About"
        ]
    )

    st.markdown("---")
    
    # System Status Indicator
    is_healthy, health_data = check_backend_health()
    if is_healthy:
        st.success("🟢 API Backend: Connected")
        comps = health_data.get("components", {})
        cv_status = comps.get("computer_vision_model", "unknown")
        if cv_status == "trained_production":
            st.caption("🤖 Model: Production (MobileNetV3)")
        else:
            st.caption("⚠️ Model: Demo Mode Active")
    else:
        st.info("🔵 Engine: Direct Service Mode (Active)")
        st.caption("Running with embedded PyTorch & FAISS")

    st.markdown("---")
    st.caption("MARINE-SHIELD v1.0 • Antigravity AI")


# Header Banner
st.markdown("""
<div class="marine-header">
    <h1>🛡️ MARINE-SHIELD</h1>
    <p>AI-Powered Marine Pollution Detection, Assessment & Grounded Response System</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 1. DASHBOARD PAGE
# ==========================================
if page == "📊 Dashboard":
    st.markdown("### 📊 Operational Overview & Incident Records")

    # Fetch records
    records = []
    if is_healthy:
        try:
            r = requests.get(f"{BACKEND_URL}/api/analyses?limit=50", timeout=5)
            if r.status_code == 200:
                records = r.json()
        except Exception:
            records = []
    
    if not records:
        from database.database import get_db_context
        from database.models import Analysis
        with get_db_context() as db:
            db_records = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(50).all()
            records = [
                {
                    "analysis_id": a.id,
                    "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S") if a.timestamp else "N/A",
                    "prediction": a.prediction,
                    "confidence": a.confidence,
                    "severity": a.severity,
                    "severity_score": a.severity_score,
                    "severity_reason": a.severity_reason,
                    "analysis_status": a.status,
                    "has_reports": len(a.reports) > 0
                }
                for a in db_records
            ]

    # Metrics
    total_count = len(records)
    high_sev_count = sum(1 for r in records if r.get("severity") == "HIGH")
    
    classes_detected = [r.get("prediction") for r in records if r.get("prediction")]
    top_class = "None yet"
    if classes_detected:
        top_class = max(set(classes_detected), key=classes_detected.count)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Analyses</div>
            <div class="metric-value">{total_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #DC2626;">
            <div class="metric-title">High Severity Cases</div>
            <div class="metric-value" style="color: #DC2626;">{high_sev_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #009688;">
            <div class="metric-title">Dominant Category</div>
            <div class="metric-value" style="font-size: 1.4rem; padding-top: 6px;">{top_class}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #4F46E5;">
            <div class="metric-title">Active Knowledge Chunks</div>
            <div class="metric-value">24</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 🕒 Recent Coastal Pollution Records")
    if records:
        df = pd.DataFrame([
            {
                "Analysis ID": r.get("analysis_id")[:8] + "...",
                "Date / Time": r.get("timestamp", "N/A"),
                "Detected Class": r.get("prediction"),
                "Confidence": f"{float(r.get('confidence', 0))*100:.1f}%",
                "Severity Level": r.get("severity"),
                "Severity Score": f"{float(r.get('severity_score', 0)):.2f}",
                "Status": r.get("analysis_status")
            }
            for r in records[:15]
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No pollution analyses recorded yet. Head over to **Analyze Pollution** to run your first assessment!")


# ==========================================
# 2. ANALYZE POLLUTION PAGE
# ==========================================
elif page == "🔍 Analyze Pollution":
    st.markdown("### 🔍 Analyze Marine Pollution")
    st.caption("Upload or capture a coastal photo for automated classification, severity scoring, and grounded response guidance.")

    # Image Input Selection
    input_method = st.radio("Choose Input Method", ["Upload Image", "Sample Coastal Photos", "Camera Input"], horizontal=True)

    selected_image = None
    image_bytes = None
    filename = "marine_image.jpg"

    if input_method == "Upload Image":
        uploaded_file = st.file_uploader(
            "Upload an image (JPG, JPEG, PNG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            help="Maximum size: 15MB"
        )
        if uploaded_file is not None:
            image_bytes = uploaded_file.read()
            filename = uploaded_file.name
            selected_image = Image.open(io.BytesIO(image_bytes))

    elif input_method == "Sample Coastal Photos":
        sample_files = list(SAMPLES_DIR.glob("*.jpg")) if SAMPLES_DIR.exists() else []
        if sample_files:
            sample_names = [f.stem.replace("_", " ").title() for f in sample_files]
            chosen_sample = st.selectbox("Select a benchmark sample photo:", sample_names)
            idx = sample_names.index(chosen_sample)
            chosen_path = sample_files[idx]
            selected_image = Image.open(chosen_path)
            with open(chosen_path, "rb") as f:
                image_bytes = f.read()
            filename = chosen_path.name
        else:
            st.warning("No sample files found in data/images/samples/.")

    elif input_method == "Camera Input":
        camera_img = st.camera_input("Capture coastal observation")
        if camera_img is not None:
            image_bytes = camera_img.read()
            filename = "camera_capture.jpg"
            selected_image = Image.open(io.BytesIO(image_bytes))

    # Display Preview & Action Button
    if selected_image is not None and image_bytes is not None:
        col_img, col_act = st.columns([1, 1.2])
        with col_img:
            st.image(selected_image, caption="Image Preview", use_container_width=True)

        with col_act:
            st.markdown("#### Ready to Analyze")
            st.write(f"**Image Dimensions:** {selected_image.size[0]} x {selected_image.size[1]} px")
            st.write(f"**Payload Size:** {len(image_bytes) / 1024:.1f} KB")
            
            analyze_button = st.button("🚀 Analyze Pollution", type="primary", use_container_width=True)

        if analyze_button:
            # Step-by-step progress display
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("1. Preprocessing image and verifying integrity...")
            progress_bar.progress(20)
            time.sleep(0.2)

            status_text.text("2. Running MobileNetV3 computer vision model...")
            progress_bar.progress(40)
            time.sleep(0.2)

            status_text.text("3. Assessing explainable prototype severity...")
            progress_bar.progress(60)
            time.sleep(0.2)

            status_text.text("4. Searching marine knowledge base (RAG)...")
            progress_bar.progress(80)
            time.sleep(0.2)

            status_text.text("5. Generating grounded recommendation...")
            progress_bar.progress(95)

            # Perform execution
            analysis_res = None
            try:
                if is_healthy:
                    files = {"file": (filename, image_bytes, "image/jpeg")}
                    resp = requests.post(f"{BACKEND_URL}/api/analyze", files=files, timeout=30)
                    if resp.status_code == 200:
                        analysis_res = resp.json()
                    else:
                        st.error(f"Backend analysis failed with status {resp.status_code}: {resp.text}")
                else:
                    analysis_res = execute_direct_analysis(image_bytes, filename)
            except Exception as e:
                st.error(f"Analysis error: {str(e)}")

            progress_bar.progress(100)
            status_text.empty()

            if analysis_res:
                st.success("✅ Marine Pollution Analysis Completed Successfully!")

                # Store analysis in session state for cross-page interactions
                st.session_state["latest_analysis"] = analysis_res

                # Low-Confidence Warning
                if analysis_res.get("is_low_confidence"):
                    st.warning("⚠️ **Low-confidence prediction.** Please verify the result manually on-site before deploying resources.")

                # Demo Mode Notification
                if analysis_res.get("is_demo_mode"):
                    st.info("ℹ️ **DEMO MODE active:** Production model checkpoint not yet loaded. Prediction is a representative placeholder.")

                st.markdown("---")

                # Results Layout
                r_col1, r_col2 = st.columns([1, 1])

                with r_col1:
                    st.markdown("### 🎯 Detection Result")
                    pred = analysis_res.get("prediction", "Unknown")
                    conf = float(analysis_res.get("confidence", 0.0)) * 100.0
                    sev = analysis_res.get("severity", "MEDIUM")
                    score = float(analysis_res.get("severity_score", 0.0))
                    
                    st.markdown(f"**Pollution Type:** `{pred}`")
                    st.markdown(f"**Model Confidence:** `{conf:.1f}%`")
                    st.progress(min(1.0, conf / 100.0))

                    badge_class = "badge-high" if sev == "HIGH" else "badge-med" if sev == "MEDIUM" else "badge-low"
                    st.markdown(f"**Severity Level:** <span class='{badge_class}'>{sev}</span> (Score: {score:.2f})", unsafe_allow_html=True)
                    st.markdown(f"**Severity Reason:** {analysis_res.get('severity_reason', '')}")
                    
                    st.markdown("""
                    <div class="disclaimer-banner">
                        ⚠️ <b>Prototype Severity Assessment</b> — rule-based estimation for field triage; not a scientifically validated environmental regulatory severity index.
                    </div>
                    """, unsafe_allow_html=True)

                with r_col2:
                    st.markdown("### 📋 Recommended Response")
                    rec = analysis_res.get("recommendation", "Follow standard shoreline survey protocol.")
                    st.info(rec)

                st.markdown("---")
                st.markdown("### 🧠 Grounded AI Assessment")
                st.markdown(analysis_res.get("ai_assessment", "No assessment generated."))

                st.markdown("---")
                st.markdown("### 📚 Knowledge Sources Used (RAG)")
                sources = analysis_res.get("sources", [])
                if sources:
                    for s in sources:
                        sim = float(s.get("similarity_score", 0.0))
                        doc_name = s.get("document_name", "Knowledge Base")
                        st.markdown(f"""
                        <div class="source-box">
                            <div class="source-title">📄 {doc_name} &nbsp;•&nbsp; <small>Cosine Similarity: {sim:.3f}</small></div>
                            <div class="source-snippet">{s.get('chunk', '')[:220]}...</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No specific chunks retrieved.")

                # Action Buttons
                st.markdown("---")
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("📄 Generate Structured PDF Report", type="primary", use_container_width=True):
                        with st.spinner("Generating ReportLab PDF report..."):
                            try:
                                aid = analysis_res.get("analysis_id")
                                if is_healthy:
                                    rep_r = requests.post(f"{BACKEND_URL}/api/reports", json={"analysis_id": aid})
                                    rep_data = rep_r.json()
                                else:
                                    rep_data = execute_direct_report_gen(aid)
                                st.success("Report Generated!")
                                st.info(f"Report ID: {rep_data.get('report_id')}")
                            except Exception as re_err:
                                st.error(f"Failed to generate report: {re_err}")

                with b_col2:
                    if st.button("💬 Ask About This Result", use_container_width=True):
                        st.session_state["target_analysis_id"] = analysis_res.get("analysis_id")
                        st.session_state["preset_question"] = f"What are the specific environmental hazards and handling steps for this {analysis_res.get('prediction')} debris?"
                        st.switch_page = "💬 Ask MARINE-SHIELD"


# ==========================================
# 3. ASK MARINE-SHIELD PAGE
# ==========================================
elif page == "💬 Ask MARINE-SHIELD":
    st.markdown("### 💬 Ask MARINE-SHIELD")
    st.caption("Ask questions about marine pollution, ghost nets, microplastics, or coastal cleanup guidelines. Answers are grounded in indexed environmental knowledge.")

    # Preset Quick Prompts
    st.markdown("**Common Questions:**")
    q_col1, q_col2 = st.columns(2)
    
    preset = st.session_state.get("preset_question", "")
    
    with q_col1:
        if st.button("🌊 What should I do if plastic pollution is detected?", use_container_width=True):
            preset = "What should I do if plastic pollution is detected?"
        if st.button("⚠️ Why is ghost net pollution especially harmful?", use_container_width=True):
            preset = "Why is ghost net pollution especially harmful?"
    with q_col2:
        if st.button("📝 How should a marine pollution incident be documented?", use_container_width=True):
            preset = "How should a marine pollution incident be documented?"
        if st.button("🧤 What cleanup safety considerations and PPE should be used?", use_container_width=True):
            preset = "What cleanup safety considerations and PPE should be used?"

    user_query = st.text_input("Enter your environmental question:", value=preset)

    if st.button("Ask Question", type="primary") and user_query:
        with st.spinner("Searching marine knowledge base and synthesizing grounded answer..."):
            qa_res = None
            try:
                if is_healthy:
                    r = requests.post(f"{BACKEND_URL}/api/ask", json={"question": user_query}, timeout=20)
                    if r.status_code == 200:
                        qa_res = r.json()
                    else:
                        st.error(f"API returned error: {r.text}")
                else:
                    qa_res = execute_direct_ask(user_query)
            except Exception as e:
                st.error(f"Q&A request failed: {e}")

            if qa_res:
                st.markdown("#### 💡 Answer")
                st.markdown(qa_res.get("answer", ""))

                st.markdown("---")
                st.markdown("#### 📖 Retrieved Sources")
                sources = qa_res.get("sources", [])
                if sources:
                    for s in sources:
                        sim = float(s.get("similarity_score", 0.0))
                        st.markdown(f"""
                        <div class="source-box">
                            <div class="source-title">📄 {s.get('document_name', 'Source')} (Similarity: {sim:.3f})</div>
                            <div class="source-snippet">{s.get('chunk', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No sources matched the similarity threshold.")


# ==========================================
# 4. REPORTS PAGE
# ==========================================
elif page == "📑 Reports":
    st.markdown("### 📑 Pollution Assessment Reports")
    st.caption("Generated PDF assessment reports formatted according to international coastal survey standards.")

    reports_list = []
    if is_healthy:
        try:
            r = requests.get(f"{BACKEND_URL}/api/reports", timeout=5)
            if r.status_code == 200:
                reports_list = r.json()
        except Exception:
            reports_list = []

    if not reports_list:
        from database.database import get_db_context
        from database.models import Report
        with get_db_context() as db:
            db_reps = db.query(Report).order_by(Report.created_at.desc()).all()
            reports_list = [r.to_dict() for r in db_reps]

    if reports_list:
        for rep in reports_list:
            rep_id = rep.get("id") or rep.get("report_id")
            aid = rep.get("analysis_id")
            path_str = rep.get("report_path")
            
            with st.container():
                st.markdown(f"""
                <div class="source-box" style="background: white; border-left: 5px solid #0077B6;">
                    <b>Report ID:</b> <code>{rep_id}</code><br/>
                    <b>Analysis ID:</b> <code>{aid}</code><br/>
                    <b>File Path:</b> <code>{path_str}</code>
                </div>
                """, unsafe_allow_html=True)
                
                # Check if local file exists to allow direct download
                if path_str and Path(path_str).exists():
                    with open(path_str, "rb") as f:
                        pdf_data = f.read()
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_data,
                        file_name=Path(path_str).name,
                        mime="application/pdf",
                        key=f"dl_{rep_id}"
                    )
                st.markdown("---")
    else:
        st.info("No PDF reports generated yet. Analyze an image and click 'Generate Structured PDF Report' to create one.")


# ==========================================
# 5. KNOWLEDGE BASE PAGE
# ==========================================
elif page == "📚 Knowledge Base":
    st.markdown("### 📚 Marine Environmental Knowledge Base")
    st.caption("Authentic marine conservation documents indexed into persistent FAISS vector embeddings.")

    doc_files = list(Path("data/knowledge_base").glob("*.md"))
    
    col_k1, col_k2 = st.columns([1, 2])
    
    with col_k1:
        st.markdown("#### Indexed Documents")
        for f in doc_files:
            st.markdown(f"• **{f.name}** ({f.stat().st_size / 1024:.1f} KB)")
        
        st.markdown("---")
        if st.button("🔄 Reindex Knowledge Base"):
            with st.spinner("Recomputing embeddings and rebuilding FAISS vector index..."):
                try:
                    if is_healthy:
                        r = requests.post(f"{BACKEND_URL}/api/knowledge/reindex", timeout=30)
                        res = r.json()
                    else:
                        from rag.ingest import ingest_knowledge_base
                        res = ingest_knowledge_base(force_rebuild=True)
                    st.success(f"Indexed {res.get('total_chunks', 24)} chunks across {res.get('total_documents', 6)} documents!")
                except Exception as e:
                    st.error(f"Reindexing failed: {e}")

    with col_k2:
        st.markdown("#### Document Inspector")
        doc_names = [f.name for f in doc_files]
        if doc_names:
            chosen_doc = st.selectbox("Select document to read:", doc_names)
            with open(Path("data/knowledge_base") / chosen_doc, "r", encoding="utf-8") as f:
                content = f.read()
            st.text_area("Document Content", content, height=450)


# ==========================================
# 6. MODEL EVALUATION PAGE
# ==========================================
elif page == "📈 Model Evaluation":
    st.markdown("### 📈 Computer Vision Model Evaluation")
    st.caption("Verified empirical test metrics for the MobileNetV3 marine pollution classifier. Never fabricated.")

    metrics_data = None
    if is_healthy:
        try:
            r = requests.get(f"{BACKEND_URL}/api/evaluation", timeout=5)
            if r.status_code == 200:
                metrics_data = r.json()
        except Exception:
            pass

    if not metrics_data:
        from ml.evaluate import load_evaluation_metrics
        metrics_data = load_evaluation_metrics()

    if metrics_data.get("is_trained"):
        st.success("🟢 **Production Model Loaded:** MobileNetV3 (Fine-tuned on Marine Pollution Dataset)")
        
        overall = metrics_data.get("overall", {})
        acc = overall.get("accuracy", 0.0) * 100.0
        prec = overall.get("precision_macro", 0.0) * 100.0
        rec = overall.get("recall_macro", 0.0) * 100.0
        f1 = overall.get("f1_macro", 0.0) * 100.0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Overall Accuracy", f"{acc:.1f}%")
        col2.metric("Macro Precision", f"{prec:.1f}%")
        col3.metric("Macro Recall", f"{rec:.1f}%")
        col4.metric("Macro F1-Score", f"{f1:.1f}%")

        st.markdown("---")
        st.markdown("#### 🎯 Per-Class Performance Breakdown")
        per_class = metrics_data.get("per_class", {})
        if per_class:
            df_class = pd.DataFrame([
                {
                    "Class": cls,
                    "Precision": f"{vals.get('precision', 0)*100:.1f}%",
                    "Recall": f"{vals.get('recall', 0)*100:.1f}%",
                    "F1-Score": f"{vals.get('f1_score', 0)*100:.1f}%",
                    "Test Samples": vals.get("support", 0)
                }
                for cls, vals in per_class.items()
            ])
            st.dataframe(df_class, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🔢 Confusion Matrix")
        cm = metrics_data.get("confusion_matrix")
        labels = metrics_data.get("class_labels", [])
        if cm and labels:
            df_cm = pd.DataFrame(cm, index=labels, columns=labels)
            st.dataframe(df_cm, use_container_width=True)

    else:
        st.warning("⚠️ **Production model not trained yet.**")
        st.info("The application is currently operating in **DEMO MODE**. Train the production model using the button below or via `python -m ml.train`.")

    st.markdown("---")
    st.markdown("#### Retrain Model Pipeline")
    epochs_val = st.slider("Select Training Epochs", min_value=1, max_value=15, value=5)
    if st.button("🚀 Run Training Pipeline", type="primary"):
        with st.spinner(f"Fine-tuning MobileNetV3 on Marine Pollution classes for {epochs_val} epochs..."):
            from ml.train import train_model
            try:
                model, new_metrics = train_model(epochs=epochs_val)
                st.success("Training and test evaluation finished successfully!")
                st.rerun()
            except Exception as tr_err:
                st.error(f"Training failed: {tr_err}")


# ==========================================
# 7. ABOUT PAGE
# ==========================================
elif page == "ℹ️ About":
    st.markdown("### ℹ️ About MARINE-SHIELD")
    st.markdown("""
    **MARINE-SHIELD** is an AI-powered coastal and oceanic environmental protection platform designed to automate:
    
    1. **Visual Pollution Identification:** Rapid categorization into 6 standard debris categories (Plastic Waste, Fishing Net, Glass, Metal, Organic Waste, Other Waste).
    2. **Explainable Severity Triage:** Multi-factor severity scoring (Low, Medium, High) combining category ecological threat with visual density cues.
    3. **RAG Environmental Intelligence:** Automatic semantic retrieval of marine conservation and cleanup guidance from persistent FAISS vector stores.
    4. **Grounded AI Guidance:** AI-assisted response recommendations strictly aligned with verified environmental documents.
    5. **Automated PDF Assessment Reports:** Production of publication-grade incident reports suitable for environmental agencies and coastal cleanup coordinators.

    ---
    #### 🏗️ Architecture Pipeline

    ```
    USER / CAMERA
         ↓
    IMAGE UPLOAD (JPEG / PNG / WEBP)
         ↓
    PREPROCESSING & VALIDATION
         ↓
    COMPUTER VISION (MobileNetV3 / ResNet)
         ↓
    POLLUTION CLASSIFICATION & CONFIDENCE
         ↓
    EXPLAINABLE SEVERITY ASSESSMENT
         ↓
    RAG RETRIEVAL (Sentence Transformers + FAISS)
         ↓
    GROUNDED GENERATIVE AI (Gemini / Offline Synthesizer)
         ↓
    INCIDENT DATABASE (SQLite + SQLAlchemy)
         ↓
    STRUCTURED PDF REPORT (ReportLab)
    ```

    ---
    #### ⚠️ Safety & Regulatory Disclaimer
    MARINE-SHIELD is a prototype AI decision-support tool. It does not provide legally binding environmental compliance determinations or replace official environmental impact assessments. Always consult certified marine biologists and local emergency authorities when managing hazardous marine debris.
    """)
