# MARINE-SHIELD Grounded Generation Prompts

GROUNDED_SYSTEM_PROMPT = """You are MARINE-SHIELD, a marine environmental information assistant.

Use the retrieved knowledge provided in the context to answer.

Do not invent facts, statistics, regulations, laws, organizations or scientific claims.

If the context does not contain enough information, say that the available knowledge base does not contain enough information.

Clearly distinguish:
1. Computer vision prediction
2. Severity assessment
3. Retrieved factual information
4. AI-generated recommendation

Do not present AI-generated content as an official environmental assessment.
"""


def build_analysis_prompt(
    prediction: str,
    confidence: float,
    severity: str,
    severity_score: float,
    severity_reason: str,
    retrieved_chunks: list
) -> str:
    """Format prompt for generating grounded assessment of detected marine pollution."""
    context_blocks = []
    for i, c in enumerate(retrieved_chunks, 1):
        source = c.get("source", "Knowledge Base")
        doc = c.get("document_name", "Marine Reference")
        text = c.get("chunk", "")
        context_blocks.append(f"[SOURCE {i}: {doc} | {source}]\n{text}")

    context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant knowledge chunks found in the database."

    prompt = f"""EVALUATION CASE:
- Computer Vision Prediction: {prediction} (Confidence: {confidence*100:.1f}%)
- Prototype Severity Assessment: {severity} (Score: {severity_score:.2f})
- Severity Reason: {severity_reason}

RETRIEVED KNOWLEDGE BASE CONTEXT:
{context_str}

INSTRUCTIONS:
Generate a structured marine environmental report adhering strictly to the retrieved context. Format your response into these exact 5 sections:

### 1. Detection Explanation
Summarize the visual identification of {prediction} with {confidence*100:.1f}% confidence and what physical materials characterize this class.

### 2. Environmental Significance
State the ecological hazards, wildlife impacts, and persistence mechanisms based directly on the provided knowledge sources.

### 3. Recommended Response
Outline actionable shoreline cleanup, personal protective equipment (PPE), and disposal/segregation procedures from the retrieved guidance.

### 4. Monitoring Considerations
Detail specific observations (e.g., biofouling, coordinates, transect density) surveyors should record for coastal monitoring.

### 5. Limitations
Explicitly state that this is an AI-assisted prototype analysis and requires field verification by qualified marine personnel.
"""
    return prompt


def build_qa_prompt(question: str, retrieved_chunks: list) -> str:
    """Format prompt for answering user environmental questions grounded in knowledge base."""
    context_blocks = []
    for i, c in enumerate(retrieved_chunks, 1):
        source = c.get("source", "Knowledge Base")
        doc = c.get("document_name", "Marine Reference")
        text = c.get("chunk", "")
        context_blocks.append(f"[SOURCE {i}: {doc} | {source}]\n{text}")

    context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant context found."

    prompt = f"""USER QUESTION:
{question}

RETRIEVED KNOWLEDGE BASE CONTEXT:
{context_str}

INSTRUCTIONS:
Answer the user's question directly, accurately, and strictly using the retrieved knowledge provided above.
If the context does not contain sufficient information to answer fully, explicitly state: "The available knowledge base does not contain enough information to address this specific question."
Cite the relevant source documents (e.g., [KB-DOC-001]) where applicable.
"""
    return prompt
