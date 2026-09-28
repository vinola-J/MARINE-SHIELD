from pathlib import Path
from reports.report_generator import generate_pollution_pdf_report


def test_pdf_report_creation():
    data = {
        "id": "test_unit_001",
        "timestamp": "2026-09-28 10:00:00 UTC",
        "prediction": "Metal",
        "confidence": 0.92,
        "severity": "MEDIUM",
        "severity_score": 0.65,
        "severity_reason": "Oxidized tin and beverage cans near coastal rocks.",
        "ai_assessment": "### 1. Detection Explanation\nMetal detected.\n### 2. Environmental Significance\nCorrosion hazard.",
        "recommendation": "Use heavy leather-palmed work gloves to segregate aluminum and steel.",
        "sources": [
            {
                "document_name": "KB-DOC-003 (Marine Glass & Metal)",
                "category": "Coastal Litter",
                "similarity_score": 0.88
            }
        ]
    }

    pdf_path = generate_pollution_pdf_report(data, output_filename="unit_test_report.pdf")
    path_obj = Path(pdf_path)
    
    assert path_obj.exists()
    assert path_obj.stat().st_size > 1000  # Non-trivial PDF output
