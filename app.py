
import html
import json
import re

import pymupdf
import requests
import streamlit as st

from scopeguard import (
    find_explicit_exclusion,
    find_explicit_inclusion,
    quote_is_verified,
)


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:1b"

st.set_page_config(
    page_title="ScopeGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# NEO-BRUTALISM UI
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --cream: #fff9ed;
        --ink: #171717;
        --pink: #ffb8d0;
        --purple: #c8b6ff;
        --teal: #a8e6cf;
        --yellow: #ffe66d;
        --paper: #ffffff;
    }

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--ink);
    }

    .stApp { background: var(--cream); }

    .block-container {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        color: var(--ink) !important;
        font-weight: 700 !important;
        letter-spacing: -1px;
    }

    .brand {
        display: inline-block;
        background: var(--yellow);
        border: 2px solid var(--ink);
        padding: 8px 14px;
        box-shadow: 4px 4px 0 var(--ink);
        font-family: 'DM Mono', monospace;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 24px;
    }

    .hero {
        background: var(--pink);
        border: 3px solid var(--ink);
        box-shadow: 8px 8px 0 var(--ink);
        padding: 32px;
        margin-bottom: 30px;
    }

    .hero h1 {
        font-size: clamp(36px, 5vw, 60px);
        line-height: 1.02;
        margin: 0 0 14px 0;
    }

    .hero p {
        font-size: 17px;
        max-width: 720px;
        margin-bottom: 0;
        line-height: 1.6;
    }

    .tag {
        display: inline-block;
        background: var(--paper);
        border: 2px solid var(--ink);
        padding: 5px 10px;
        margin: 0 5px 8px 0;
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        font-weight: 500;
    }

    .paper-card {
        background: var(--paper);
        border: 2px solid var(--ink);
        box-shadow: 5px 5px 0 var(--ink);
        padding: 22px;
        margin: 12px 0 22px 0;
    }

    .section-label {
        font-family: 'DM Mono', monospace;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }

    .result-card {
        background: var(--paper);
        border: 3px solid var(--ink);
        box-shadow: 7px 7px 0 var(--ink);
        padding: 24px;
        margin: 15px 0 26px 0;
        overflow-wrap: anywhere;
    }

    .result-status {
        display: inline-block;
        border: 2px solid var(--ink);
        padding: 7px 12px;
        font-family: 'DM Mono', monospace;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 12px;
    }

    .status-included { background: var(--teal); }
    .status-additional { background: var(--pink); }
    .status-unclear { background: var(--yellow); }

    .evidence {
        background: #f4f0ff;
        border-left: 5px solid #8d6cff;
        padding: 16px;
        margin: 12px 0;
        line-height: 1.65;
        overflow-wrap: anywhere;
    }

    .reply {
        background: #e8f8ef;
        border: 2px solid var(--ink);
        padding: 18px;
        line-height: 1.7;
        overflow-wrap: anywhere;
    }

    .small-note {
        color: #555;
        font-size: 13px;
        line-height: 1.6;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        background: var(--yellow);
        color: var(--ink);
        border: 2px solid var(--ink);
        border-radius: 0;
        box-shadow: 4px 4px 0 var(--ink);
        font-weight: 700;
        min-height: 48px;
        transition: transform 0.1s ease, box-shadow 0.1s ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        color: var(--ink);
        transform: translate(2px, 2px);
        box-shadow: 2px 2px 0 var(--ink);
        border-color: var(--ink);
    }

    div[data-testid="stFileUploader"] {
        background: #fff;
        border: 2px dashed var(--ink);
        padding: 12px;
    }

    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="input"] input {
        background: #fff;
        border: 2px solid var(--ink);
        border-radius: 0;
    }

    hr { border-color: var(--ink); }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TEXT UTILITIES
# ============================================================

def safe_text(value):
    """Escape dynamic text before displaying it as HTML."""
    return html.escape(str(value or ""))


def normalize_text(value):
    """Normalize whitespace and case for evidence retrieval."""
    return " ".join(str(value or "").lower().split())


def find_evidence_candidates(
    agreement_text,
    client_request,
    limit=5,
):
    """
    Retrieve potentially relevant agreement paragraphs.

    These candidates help the model search the agreement. They are
    not proof that a feature is included or excluded.
    """
    request_words = set(
        re.findall(r"[a-z0-9]+", normalize_text(client_request))
    )

    stop_words = {
        "the", "and", "for", "with", "that", "this", "from",
        "have", "has", "had", "will", "would", "could", "should",
        "please", "need", "want", "client", "request", "make",
        "add", "also", "into", "our", "your", "you", "are",
        "was", "were", "can", "able", "now", "but",
    }

    request_words -= stop_words

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(
            r"\n\s*\n|\n",
            agreement_text or "",
        )
        if paragraph.strip()
    ]

    scored = []

    for paragraph in paragraphs:
        paragraph_words = set(
            re.findall(r"[a-z0-9]+", normalize_text(paragraph))
        )

        overlap = request_words.intersection(paragraph_words)

        if overlap:
            score = len(overlap) / max(len(request_words), 1)
            scored.append((score, paragraph))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [
        paragraph
        for _, paragraph in scored[:limit]
    ]


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(uploaded_file):
    """Extract readable text from a PDF using PyMuPDF."""
    document = None

    try:
        document = pymupdf.open(
            stream=uploaded_file.getvalue(),
            filetype="pdf",
        )

        extracted_text = "\n\n".join(
            page.get_text("text")
            for page in document
        ).strip()

        if not extracted_text:
            return (
                "",
                "No readable text was found. The PDF may be scanned "
                "or image-only; OCR may be required.",
            )

        return extracted_text, ""

    except Exception:
        return (
            "",
            "Could not read the PDF. Please check that it is valid "
            "and try uploading it again.",
        )

    finally:
        if document is not None:
            document.close()


# ============================================================
# FALLBACK QUESTIONS AND CLIENT REPLY
# ============================================================

def fallback_questions(classification):
    if classification == "INCLUDED":
        return [
            "Can you confirm the expected behavior and acceptance criteria?",
            "Are there any design or technical constraints to follow?",
            "What delivery date should we confirm?",
        ]

    if classification == "POTENTIALLY ADDITIONAL":
        return [
            "Would you like a separate estimate for this additional work?",
            "What deadline do you have in mind for the requested change?",
            "Should the existing deliverables remain unchanged?",
        ]

    return [
        "Could you clarify the exact functionality you expect?",
        "Is this replacing an existing deliverable or adding a new one?",
        "Can we review the relevant agreement section together?",
    ]


def fallback_reply(classification):
    if classification == "INCLUDED":
        return (
            "Thanks for sharing the request. Based on the agreement "
            "wording reviewed, this appears to be part of the agreed "
            "deliverables. Could you confirm the expected behavior and "
            "acceptance criteria so I can plan the implementation?"
        )

    if classification == "POTENTIALLY ADDITIONAL":
        return (
            "Thanks for sharing the request. It may fall outside the "
            "currently agreed scope based on the wording reviewed. "
            "I'd be happy to discuss the requirements and provide a "
            "separate estimate, including the timeline, before proceeding."
        )

    return (
        "Thanks for sharing the request. I want to make sure we interpret "
        "the original agreement consistently. Could we clarify the "
        "expected functionality and review the relevant deliverables "
        "before confirming whether this is included or requires a "
        "scope adjustment?"
    )


# ============================================================
# OLLAMA ANALYSIS
# ============================================================

def analyze_with_ollama(
    agreement_text,
    client_request,
    candidates,
):
    """Ask the local Ollama model for a structured analysis."""

    candidate_text = "\n\n".join(
        f"[Candidate {index + 1}]\n{paragraph}"
        for index, paragraph in enumerate(candidates)
    )

    if not candidate_text:
        candidate_text = "No relevant paragraphs were retrieved."

    prompt = f"""
You are ScopeGuard AI, an assistant that helps freelancers review
whether a client's new request appears to fit an existing agreement.

This is business decision support, not legal advice.

ORIGINAL AGREEMENT TEXT:
{agreement_text[:18000]}

CLIENT'S NEW REQUEST:
{client_request}

POTENTIALLY RELEVANT AGREEMENT PARAGRAPHS:
{candidate_text}

Instructions:
1. Classify the request as exactly one of:
   INCLUDED
   POTENTIALLY ADDITIONAL
   UNCLEAR

2. Use INCLUDED only if the agreement clearly supports that the
   requested work is included.

3. Use POTENTIALLY ADDITIONAL if the agreement clearly excludes
   the work or strong evidence indicates it is outside the scope.

4. Use UNCLEAR when the available agreement wording is insufficient,
   ambiguous, or does not address the request.

5. Do not invent agreement terms, clauses, prices, or deadlines.

6. The evidence_quote must be copied exactly from the agreement.
   If no relevant exact sentence can be identified, return an empty
   string for evidence_quote.

7. Keep the reasoning short and explain uncertainty honestly.

8. Provide up to three practical clarifying questions.

9. Provide a polite, professional reply the freelancer could send
   to the client. Do not make threats or assert legal conclusions.

Return ONLY valid JSON with this structure:
{{
  "classification": "UNCLEAR",
  "reasoning": "Short explanation",
  "evidence_quote": "",
  "questions": [
    "Question one?",
    "Question two?"
  ],
  "client_reply": "A polite message to the client"
}}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1},
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=180,
    )

    response.raise_for_status()

    raw_output = response.json().get("response", "")

    if not raw_output:
        raise ValueError("The AI model returned an empty response.")

    result = json.loads(raw_output)

    allowed_classifications = {
        "INCLUDED",
        "POTENTIALLY ADDITIONAL",
        "UNCLEAR",
    }

    classification = str(
        result.get("classification", "UNCLEAR")
    ).strip().upper()

    if classification not in allowed_classifications:
        classification = "UNCLEAR"

    quote = str(
        result.get("evidence_quote", "")
    ).strip()

    # Never present an unverified model quotation as evidence.
    verified = bool(
        quote and quote_is_verified(quote, agreement_text)
    )

    if not verified:
        quote = ""

    questions = result.get("questions", [])

    if not isinstance(questions, list):
        questions = []

    questions = [
        str(question).strip()
        for question in questions
        if str(question).strip()
    ][:3]

    return {
        "classification": classification,
        "reasoning": str(result.get("reasoning", "")).strip(),
        "evidence_quote": quote,
        "verified": verified,
        "questions": questions,
        "client_reply": str(
            result.get("client_reply", "")
        ).strip(),
    }


# ============================================================
# MAIN ANALYSIS PIPELINE
# ============================================================

def analyze_scope(agreement_text, client_request):
    """
    Analyze a client request.

    Priority:
    1. Explicit exclusion found by rule-based checks.
    2. Explicit inclusion found by rule-based checks.
    3. Local model analysis with quotation verification.
    4. Safe UNCLEAR fallback if the model fails.
    """

    candidates = find_evidence_candidates(
        agreement_text,
        client_request,
    )

    exclusion_quote = find_explicit_exclusion(
        agreement_text,
        client_request,
    )

    inclusion_quote = find_explicit_inclusion(
        agreement_text,
        client_request,
    )

    # An explicit exclusion takes priority over an inclusion match.
    if exclusion_quote:
        classification = "POTENTIALLY ADDITIONAL"

        return {
            "classification": classification,
            "reasoning": (
                "The agreement contains wording that appears to "
                "explicitly exclude a feature mentioned in the request. "
                "Discuss a scope change, cost, and timeline before proceeding."
            ),
            "evidence_quote": exclusion_quote,
            "verified": True,
            "questions": fallback_questions(classification),
            "client_reply": fallback_reply(classification),
            "evidence_note": (
                "This exact sentence was found in the agreement. Review "
                "surrounding clauses, exceptions, and amendments."
            ),
            "source": "agreement rule check",
        }

    if inclusion_quote:
        classification = "INCLUDED"

        return {
            "classification": classification,
            "reasoning": (
                "The agreement contains wording that appears to include "
                "the requested feature among the deliverables."
            ),
            "evidence_quote": inclusion_quote,
            "verified": True,
            "questions": fallback_questions(classification),
            "client_reply": fallback_reply(classification),
            "evidence_note": (
                "This sentence supports treating the feature as included. "
                "Check other clauses for limits, conditions, and exclusions."
            ),
            "source": "agreement rule check",
        }

    try:
        result = analyze_with_ollama(
            agreement_text,
            client_request,
            candidates,
        )

        classification = result["classification"]
        quote = result["evidence_quote"]

        verified = bool(
            quote and quote_is_verified(quote, agreement_text)
        )

        result.update({
            "evidence_quote": quote if verified else "",
            "verified": verified,
            "reasoning": result["reasoning"] or (
                "The available agreement wording needs further review."
            ),
            "questions": result["questions"] or (
                fallback_questions(classification)
            ),
            "client_reply": result["client_reply"] or (
                fallback_reply(classification)
            ),
            "evidence_note": (
                "The quotation was matched exactly against the agreement."
                if verified
                else (
                    "No exact quotation from the model could be verified "
                    "against the agreement. This does not establish whether "
                    "the request is included or excluded."
                )
            ),
            "source": "local AI analysis",
        })

        return result

    except requests.exceptions.ConnectionError:
        reason = (
            "The local AI service could not be reached. Start Ollama and "
            "ensure the configured model is available. The rule-based "
            "checks found no clear match."
        )

    except requests.exceptions.Timeout:
        reason = (
            "The local AI model took too long to respond. Try again or "
            "check whether Ollama has finished loading the model."
        )

    except (
        requests.exceptions.RequestException,
        ValueError,
        json.JSONDecodeError,
    ):
        reason = (
            "The AI analysis could not be completed. Review the agreement "
            "manually and try again."
        )

    return {
        "classification": "UNCLEAR",
        "reasoning": reason,
        "evidence_quote": "",
        "verified": False,
        "questions": fallback_questions("UNCLEAR"),
        "client_reply": fallback_reply("UNCLEAR"),
        "evidence_note": (
            "No exact quotation was verified because model analysis "
            "did not finish."
        ),
        "source": "fallback",
    }


# ============================================================
# RESULT RENDERING
# ============================================================

def render_result_card(result):
    classification = result.get("classification", "UNCLEAR")

    status_classes = {
        "INCLUDED": "status-included",
        "POTENTIALLY ADDITIONAL": "status-additional",
        "UNCLEAR": "status-unclear",
    }

    status_class = status_classes.get(
        classification,
        "status-unclear",
    )

    st.markdown(
        f"""
        <div class="result-card">
            <div class="section-label">01 / Scope assessment</div>
            <div class="result-status {status_class}">
                {safe_text(classification)}
            </div>
            <h3>What this means</h3>
            <p>{safe_text(result.get("reasoning", ""))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 02 / Agreement evidence")

    quote = result.get("evidence_quote", "")
    verified = result.get("verified", False)

    if quote and verified:
        st.markdown(
            f"""
            <div class="evidence">
                <div class="section-label">Exact verified quotation</div>
                “{safe_text(quote)}”
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info(
            "No exact agreement quotation was verified. Do not treat "
            "the classification as proven by the agreement."
        )

    st.markdown(
        f'<p class="small-note">'
        f'{safe_text(result.get("evidence_note", ""))}</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### 03 / Questions to clarify")

    for question in result.get("questions", []):
        st.markdown(f"- {safe_text(question)}")

    st.markdown("### 04 / Suggested client reply")

    reply = result.get("client_reply") or fallback_reply(classification)

    st.markdown(
        f'<div class="reply">'
        f'{safe_text(reply).replace(chr(10), "<br>")}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.button(
        "Show reply to copy",
        key="copy_reply_button",
        on_click=lambda: st.session_state.update(
            {"reply_to_copy": reply}
        ),
    )

    if st.session_state.get("reply_to_copy"):
        st.code(
            st.session_state["reply_to_copy"],
            language=None,
        )
        st.caption(
            "Select and copy the reply above. Review it before sending."
        )


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    """
    <div class="brand">🛡️ SCOPEGUARD AI / FREELANCER TOOLKIT</div>

    <div class="hero">
        <div>
            <span class="tag">LOCAL AI</span>
            <span class="tag">PDF ANALYSIS</span>
            <span class="tag">SCOPE CLARITY</span>
        </div>
        <h1>Protect your scope.<br>Keep your cool.</h1>
        <p>
            Compare a client's new request with your original agreement.
            Find relevant wording, spot potential scope changes, and
            prepare a professional response before you commit.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2)

with left:
    st.markdown(
        """
        <div class="paper-card">
            <div class="section-label">01 / Upload</div>
            <h3>Bring your agreement</h3>
            <p>Upload a text-based PDF or paste the agreement directly.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="paper-card">
            <div class="section-label">02 / Compare</div>
            <h3>Check the new request</h3>
            <p>Review evidence, clarify ambiguity, and draft a reply.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# INPUT FORM
# ============================================================

st.markdown("## Let's review the request")

uploaded_pdf = st.file_uploader(
    "Upload your agreement (PDF)",
    type=["pdf"],
    help="Text-based PDFs work best. Scanned PDFs may need OCR.",
)

pasted_agreement = st.text_area(
    "Or paste the agreement text",
    height=220,
    placeholder=(
        "Paste the original proposal, agreement, deliverables, "
        "exclusions, and relevant terms here..."
    ),
)

client_request = st.text_area(
    "What is the client asking for now?",
    height=130,
    placeholder=(
        "Example: The client wants a new payment gateway and "
        "a mobile application in addition to the website."
    ),
)

analyze_clicked = st.button(
    "Analyze request →",
    use_container_width=True,
)


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze_clicked:
    agreement_text = pasted_agreement.strip()
    pdf_error = ""

    if uploaded_pdf is not None:
        extracted_text, pdf_error = extract_pdf_text(uploaded_pdf)

        if extracted_text:
            if agreement_text:
                agreement_text += "\n\n" + extracted_text
            else:
                agreement_text = extracted_text

    if pdf_error:
        st.warning(pdf_error)

    if not agreement_text:
        st.error(
            "Please upload a readable PDF or paste your agreement text."
        )

    elif not client_request.strip():
        st.error("Please describe the client's new request.")

    else:
        with st.spinner(
            "Reviewing the agreement and checking the request..."
        ):
            result = analyze_scope(
                agreement_text,
                client_request.strip(),
            )

        st.session_state["scopeguard_result"] = result

        st.divider()
        render_result_card(result)

        st.markdown(
            """
            <p class="small-note">
                ScopeGuard AI provides business decision support, not
                legal advice. Automated keyword checks and AI analysis
                can miss context, exceptions, definitions, or amendments.
                Review the complete agreement before deciding how to
                respond to your client.
            </p>
            """,
            unsafe_allow_html=True,
        )

elif st.session_state.get("scopeguard_result"):
    # Preserve the latest result after Streamlit reruns.
    st.divider()
    render_result_card(st.session_state["scopeguard_result"])


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:12px 0;">
        <div class="section-label">Built for freelancers</div>
        <p>
            ScopeGuard AI · Local-first scope review ·
            Make the agreement easier to discuss.
        </p>
        <p class="small-note">
            Business decision support only. Not legal advice.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
