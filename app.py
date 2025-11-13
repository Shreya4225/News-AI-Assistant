# ui/app.py
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from langgraph_workflow.graph_definition import run_newsletter_workflow
from utils.logger import setup_logger

# Setup
st.set_page_config(page_title="AI Newsletter Assistant", layout="wide")
logger = setup_logger("ui_app")

DATA_DIR = Path("data")
SUBSCRIBERS_FILE = DATA_DIR / "subscribers.json"
NEWSLETTER_FILE = DATA_DIR / "cache/newsletter.html"
SETTINGS_FILE = Path("config/settings.py")

# --- Helper Functions ---
def get_subscriber_count():
    if SUBSCRIBERS_FILE.exists():
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            subscribers = json.load(f)
        return len(subscribers)
    return 0

def get_last_newsletter_time():
    if NEWSLETTER_FILE.exists():
        modified_time = datetime.fromtimestamp(NEWSLETTER_FILE.stat().st_mtime)
        return modified_time.strftime("%Y-%m-%d %H:%M:%S")
    return "No newsletter generated yet."

def load_newsletter_preview():
    if NEWSLETTER_FILE.exists():
        return NEWSLETTER_FILE.read_text(encoding="utf-8")
    return "<p>No newsletter available yet. Please generate one.</p>"

def update_topic(new_topic):
    settings_path = Path("config/settings.py")
    with open(settings_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(settings_path, "w", encoding="utf-8") as f:
        for line in lines:
            if line.strip().startswith("TOPIC"):
                f.write(f"TOPIC = '{new_topic}'\n")
            else:
                f.write(line)
    st.success(f"✅ Topic updated to '{new_topic}'")

# --- UI Layout ---
st.title("🧠 AI Newsletter Assistant")
st.markdown("### Your automated daily AI newsletter system")

tabs = st.tabs(["🏠 Home Overview", "📰 Newsletter Preview", "📤 Send Now", "🧠 Settings"])

# 🏠 Home Overview
with tabs[0]:
    st.subheader("📊 Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👥 Total Subscribers", get_subscriber_count())
    with col2:
        st.metric("🕒 Last Newsletter Generated", get_last_newsletter_time())

    st.info("Your system automatically fetches, summarizes, and emails AI news every day at 9:00 AM.")

# 📰 Newsletter Preview
# with tabs[1]:
#     st.subheader("📰 Latest Newsletter Preview")
#     html_content = load_newsletter_preview()
#     st.components.v1.html(html_content, height=600, scrolling=True)

# 📰 Newsletter Preview
with tabs[1]:
    st.subheader("📰 Latest Newsletter Preview")

    html_content = load_newsletter_preview()

    # Wrap newsletter HTML in a dark container with white text
    styled_html = f"""
    <div style="
        background-color: #0e1117;
        color: white;
        padding: 25px;
        border-radius: 12px;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.6;
    ">
        {html_content}
    </div>
    """

    st.components.v1.html(styled_html, height=600, scrolling=True)


# 🚀 Manual Trigger
with tabs[2]:
    st.subheader("🚀 Generate & Send Newsletter Now")
    st.markdown("Click the button below to manually run the full workflow (Fetch → Summarize → Write → Mail).")

    if st.button("Run Newsletter Workflow"):
        with st.spinner("Running full newsletter pipeline... please wait ⏳"):
            try:
                result = run_newsletter_workflow()
                st.success("✅ Newsletter generated and sent successfully!")
                st.json(result)
                logger.info("Manual trigger executed successfully from UI.")
            except Exception as e:
                st.error(f"❌ Workflow failed: {e}")
                logger.error(f"Manual trigger failed: {e}")

# 🧠 Settings Tab
with tabs[3]:
    st.subheader("⚙️ Settings")

    st.write("Change newsletter topic (default: Artificial Intelligence)")
    current_topic = "Artificial Intelligence"

    # Read current topic from config/settings.py
    settings_path = Path("config/settings.py")
    if settings_path.exists():
        for line in settings_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("TOPIC"):
                current_topic = line.split("=")[1].strip().replace("'", "")

    new_topic = st.text_input("Newsletter Topic", value=current_topic)
    if st.button("Update Topic"):
        update_topic(new_topic)
