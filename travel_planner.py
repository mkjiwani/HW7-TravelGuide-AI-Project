import os
from datetime import datetime
from textwrap import dedent

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# PDF generation
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
)

# -------------------------
# ENV & CLIENT
# -------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------
# STREAMLIT CONFIG
# -------------------------
st.set_page_config(
    page_title="Personalized Travel Planner",
    page_icon="✈️",
    layout="centered",
)

FORM_KEYS = [
    "destination",
    "num_days",
    "interests",
    "guardrails",
]

def init_form_state():
    for k in FORM_KEYS:
        st.session_state.setdefault(k, "")
    st.session_state.setdefault("plan_md", "")

def reset_all_callback():
    for k in FORM_KEYS:
        st.session_state[k] = ""
    st.session_state["plan_md"] = ""
    st.session_state.pop("last_model_used", None)
    st.session_state.pop("last_usage", None)

init_form_state()

st.title("✈️ Personalized Travel Planner")
st.caption("AI-Powered Custom Itineraries")

with st.expander("What this app does", expanded=False):
    st.markdown(
        "- Collects your destination, duration, and preferences\n"
        "- Produces a **day-by-day itinerary** including sights, food, and logistics\n"
        "- Respects your **guardrails** (e.g., accessibility, kid-friendly, no walking)\n"
        "- Generates a **downloadable PDF** for your trip"
    )

# -------------------------
# PROMPTS
# -------------------------
SYSTEM_PROMPT = dedent("""
You are an expert TRAVEL PLANNER and CONCIERGE. 
Requirements:
- Produce a detailed, day-by-day itinerary.
- Include specific recommendations for food, historic sites, and activities based on user interests.
- Strictly adhere to the user's guardrails (e.g., if 'no walking', suggest transport or stationary activities).
- Provide a balanced mix of popular landmarks and hidden gems.
Output format in Markdown with these top-level H2 sections (##):
  ## Trip Overview
  ## Daily Itinerary
  ## Dining & Cuisine Recommendations
  ## Logistics & Transport Tips
  ## Important Local Info (Safety/Weather)
""").strip()

def build_user_prompt(destination, num_days, interests, guardrails):
    return dedent(f"""
    TRIP DETAILS
    - Destination: {destination}
    - Duration: {num_days} days
    - Special Interests: {interests}
    
    CONSTRAINTS & GUARDRAILS
    - {guardrails or 'None specified'}

    INSTRUCTIONS
    - Create a plan for exactly {num_days} days.
    - Ensure every activity aligns with the interests: {interests}.
    - Ensure every activity respects the guardrails: {guardrails}.
    - Keep the tone helpful and exciting.
    """).strip()

# -------------------------
# API LOGIC
# -------------------------
FALLBACK_MODELS = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"] 

def get_travel_plan(user_prompt):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    
    last_error = None
    for model_name in FALLBACK_MODELS:
        try:
            comp = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=2500,
            )
            text = comp.choices[0].message.content
            if text.strip():
                st.session_state["last_model_used"] = model_name
                return text
        except Exception as e:
            last_error = e
            continue
    raise RuntimeError(f"Failed to generate plan: {last_error}")

# -------------------------
# PDF HELPERS
# -------------------------
def markdown_to_flowables(md_text, styles):
    flow = []
    body = styles["BodyText"]
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=12, spaceAfter=6)
    
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            flow.append(Spacer(1, 6))
            i += 1
            continue
        if line.startswith("## "):
            flow.append(Paragraph(line[3:].strip(), h2))
            i += 1
            continue
        if line.lstrip().startswith(("-", "*", "•")):
            items = []
            while i < len(lines) and lines[i].lstrip().startswith(("-", "*", "•")):
                bullet_text = lines[i].lstrip()[1:].strip()
                items.append(ListItem(Paragraph(bullet_text, body), leftIndent=12))
                i += 1
            flow.append(ListFlowable(items, bulletType="bullet", start="•", leftIndent=6))
            continue
        flow.append(Paragraph(line, body))
        i += 1
    return flow

def write_pdf(markdown_text, filename="travel_itinerary.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=LETTER,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )
    styles = getSampleStyleSheet()
    header = ParagraphStyle("Header", parent=styles["Title"], fontSize=18, spaceAfter=12)
    
    story = [Paragraph("Your Travel Itinerary", header)]
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))
    story.append(Spacer(1, 10))
    story.extend(markdown_to_flowables(markdown_text, styles))
    doc.build(story)
    return filename

# -------------------------
# INPUT FORM
# -------------------------
with st.form("travel_inputs"):
    st.text_input("1) Destination to Travel", placeholder="e.g., Tokyo, Japan", key="destination")
    st.text_input("2) Number of Days", placeholder="e.g., 5 days", key="num_days")
    st.text_area("3) Special Interests", placeholder="e.g., Museums, Food & Cuisine, Photography", key="interests")
    st.text_area("4) Guardrails / Preferences", placeholder="e.g., Wheelchair accessible, kid-friendly, no spicy food", key="guardrails")
    
    submitted = st.form_submit_button("Generate Travel Plan")

# -------------------------
# MAIN ACTION
# -------------------------
if submitted:
    if not (st.session_state["destination"] and st.session_state["num_days"]):
        st.warning("Please provide at least a Destination and Number of Days.")
    else:
        with st.spinner("Crafting your perfect itinerary..."):
            u_prompt = build_user_prompt(
                st.session_state["destination"],
                st.session_state["num_days"],
                st.session_state["interests"],
                st.session_state["guardrails"]
            )
            try:
                st.session_state["plan_md"] = get_travel_plan(u_prompt)
            except Exception as e:
                st.error(f"Error: {e}")

if st.session_state["plan_md"]:
    st.success("Itinerary Ready!")
    st.markdown(st.session_state["plan_md"])
    
    # PDF Export
    try:
        pdf_path = write_pdf(st.session_state["plan_md"])
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Itinerary PDF",
                data=f.read(),
                file_name="travel_plan.pdf",
                mime="application/pdf",
            )
    except Exception as e:
        st.error(f"PDF generation error: {e}")

st.divider()
st.button("🔁 Reset Form & Clear Plan", type="secondary", on_click=reset_all_callback)