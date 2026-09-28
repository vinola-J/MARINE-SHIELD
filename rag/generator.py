import os
from typing import List, Dict, Any, Tuple, Optional
from rag.config import LLM_PROVIDER, LLM_MODEL, LLM_API_KEY
from rag.prompts import GROUNDED_SYSTEM_PROMPT, build_analysis_prompt, build_qa_prompt


def generate_offline_grounded_assessment(
    prediction: str,
    confidence: float,
    severity: str,
    severity_score: float,
    severity_reason: str,
    sources: List[Dict[str, Any]]
) -> Tuple[str, str]:
    """
    Deterministic grounded synthesizer used when LLM API keys are not configured or external API is unavailable.
    Directly extracts and synthesizes factual information from the retrieved knowledge chunks.
    
    Returns:
        (ai_assessment, recommended_response)
    """
    source_names = ", ".join(s.get("title", s.get("document_name", "Knowledge Base")) for s in sources) or "Marine Environmental Repository"
    
    # Extract excerpt highlights from top source chunks
    excerpts = []
    response_guidance = []
    monitoring_tips = []
    
    for s in sources:
        chunk = s.get("chunk", "")
        lines = [line.strip() for line in chunk.split("\n") if line.strip() and not line.startswith("#")]
        for line in lines:
            line_clean = line.lstrip("-* ").strip()
            if any(term in line_clean.lower() for term in ["ingestion", "hazard", "threat", "entanglement", "anoxia", "damage", "corrosion", "persists"]):
                if len(line_clean) > 30 and len(excerpts) < 3:
                    excerpts.append(line_clean)
            elif any(term in line_clean.lower() for term in ["ppe", "glove", "collect", "separate", "segregat", "bucket", "cutter", "retrieval"]):
                if len(line_clean) > 30 and len(response_guidance) < 3:
                    response_guidance.append(line_clean)
            elif any(term in line_clean.lower() for term in ["transect", "record", "gps", "monitor", "density", "biofouling", "tally"]):
                if len(line_clean) > 30 and len(monitoring_tips) < 2:
                    monitoring_tips.append(line_clean)

    # Fallback text if chunk didn't yield specific matching lines
    if not excerpts:
        excerpts.append(f"Marine {prediction.lower()} presents ongoing physical and ecological threats to coastal ecosystems and marine organisms through ingestion and habitat disruption.")
    if not response_guidance:
        response_guidance.append("Utilize heavy puncture-resistant gloves and sturdy closed-toe footwear during shoreline cleanup; segregate waste streams at the point of collection.")
    if not monitoring_tips:
        monitoring_tips.append("Document GPS coordinates, coastal tide state, and estimated item count according to standardized marine debris survey transects.")

    ai_assessment = f"""### 1. Detection Explanation
Computer vision identified **{prediction}** with **{confidence*100:.1f}% confidence**. Visual features indicate a material pattern consistent with anthropogenic marine debris.

### 2. Environmental Significance
Based on retrieved knowledge from *{source_names}*:
- {excerpts[0]}
{f"- {excerpts[1]}" if len(excerpts) > 1 else ""}
{f"- {excerpts[2]}" if len(excerpts) > 2 else ""}

### 3. Severity Triage Summary
Assessed at **{severity} Severity (Score: {severity_score:.2f})**. {severity_reason}

### 4. Monitoring Considerations
- {monitoring_tips[0]}
{f"- {monitoring_tips[1]}" if len(monitoring_tips) > 1 else ""}

### 5. Limitations
*Notice: This assessment is generated using local grounded environmental knowledge retrieval (Offline Mode). Field manual verification by coastal management personnel is recommended.*"""

    recommended_response = f"""**Actionable Field Response Protocol ({severity} Priority):**

1. **Safety & PPE:** {response_guidance[0]}
2. **Waste Segregation:** {response_guidance[1] if len(response_guidance) > 1 else "Sort collected materials into recyclable rigid containers, derelict gear, and non-recyclable residue."}
3. **Disposal & Documentation:** {response_guidance[2] if len(response_guidance) > 2 else "Log incident metadata on standard coastal survey tally sheets and ensure containment to prevent refloating."}"""

    return ai_assessment, recommended_response


def generate_offline_grounded_qa(question: str, sources: List[Dict[str, Any]]) -> str:
    """Offline grounded response synthesizer for Ask MARINE-SHIELD."""
    if not sources:
        return "The available knowledge base does not contain enough information to address this specific question. Please verify the question or ensure relevant marine documents are indexed in the knowledge base."

    answers = []
    for s in sources[:2]:
        doc_title = s.get("title", s.get("document_name", "Knowledge Base"))
        chunk_text = s.get("chunk", "")
        # Get first two clean paragraphs
        paras = [p.strip() for p in chunk_text.split("\n\n") if p.strip() and not p.startswith("#")]
        if paras:
            answers.append(f"**From {doc_title}:**\n{paras[0]}")

    joined_answer = "\n\n".join(answers)
    return f"{joined_answer}\n\n*(Grounded response synthesized from indexed marine environmental documents. Not an official legal regulation.)*"


def call_gemini_api(prompt: str, api_key: str, model_name: str = "gemini-2.5-flash") -> Optional[str]:
    """Call Google Gemini API using google-genai SDK or direct REST fallback."""
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "system_instruction": GROUNDED_SYSTEM_PROMPT,
                "temperature": 0.2
            }
        )
        return response.text
    except Exception as e:
        print(f"[LLM Warning] Gemini SDK call failed: {e}. Trying REST endpoint...")
        # Direct REST API fallback
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "systemInstruction": {"parts": [{"text": GROUNDED_SYSTEM_PROMPT}]},
                "generationConfig": {"temperature": 0.2}
            }
            res = requests.post(url, json=payload, timeout=20)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                print(f"[LLM Warning] Gemini REST returned status {res.status_code}: {res.text}")
                return None
        except Exception as rest_e:
            print(f"[LLM Error] Gemini REST call failed: {rest_e}")
            return None


def call_openai_api(prompt: str, api_key: str, model_name: str = "gpt-4o-mini") -> Optional[str]:
    """Call OpenAI API using official client."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": GROUNDED_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"[LLM Error] OpenAI API call failed: {e}")
        return None


def generate_pollution_assessment(
    prediction: str,
    confidence: float,
    severity: str,
    severity_score: float,
    severity_reason: str,
    sources: List[Dict[str, Any]]
) -> Tuple[str, str]:
    """
    Generate grounded AI explanation and recommended response.
    Routes to external LLM if configured and available, or cleanly falls back to offline grounded synthesizer.
    """
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()
    api_key = os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or LLM_API_KEY
    model_name = os.getenv("LLM_MODEL", LLM_MODEL)

    prompt = build_analysis_prompt(
        prediction=prediction,
        confidence=confidence,
        severity=severity,
        severity_score=severity_score,
        severity_reason=severity_reason,
        retrieved_chunks=sources
    )

    generated_text = None

    if provider == "gemini" and api_key:
        generated_text = call_gemini_api(prompt, api_key=api_key, model_name=model_name)
    elif provider == "openai" and api_key:
        generated_text = call_openai_api(prompt, api_key=api_key, model_name=model_name)

    if generated_text:
        # Separate response if Recommended Response section is present
        if "### 3. Recommended Response" in generated_text:
            parts = generated_text.split("### 3. Recommended Response")
            assessment = parts[0].strip()
            rest = "### 3. Recommended Response" + parts[1]
            return assessment, rest
        return generated_text, "Follow standard marine debris cleanup protocols with appropriate PPE and waste segregation."

    # Offline Grounded Fallback
    return generate_offline_grounded_assessment(
        prediction=prediction,
        confidence=confidence,
        severity=severity,
        severity_score=severity_score,
        severity_reason=severity_reason,
        sources=sources
    )


def answer_environmental_question(question: str, sources: List[Dict[str, Any]]) -> str:
    """
    Answer user question grounded strictly in retrieved context.
    Uses LLM if available, otherwise offline grounded synthesizer.
    """
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()
    api_key = os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or LLM_API_KEY
    model_name = os.getenv("LLM_MODEL", LLM_MODEL)

    prompt = build_qa_prompt(question=question, retrieved_chunks=sources)

    if provider == "gemini" and api_key:
        res = call_gemini_api(prompt, api_key=api_key, model_name=model_name)
        if res:
            return res
    elif provider == "openai" and api_key:
        res = call_openai_api(prompt, api_key=api_key, model_name=model_name)
        if res:
            return res

    return generate_offline_grounded_qa(question=question, sources=sources)
