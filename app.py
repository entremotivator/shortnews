import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI
from fpdf import FPDF
import datetime
import io

# ------------------ CONFIG ------------------
st.set_page_config(page_title="🗞️ Daily News by Topic", layout="wide")
st.title("📰 Daily News Categorized by Topic")

# Sidebar inputs
openai_api_key = st.sidebar.text_input("🔐 OpenAI API Key", type="password")
selected_date = st.sidebar.date_input("📅 Select Date", datetime.date.today())
num_articles = st.sidebar.slider("📰 Articles per Topic", 3, 15, 5)
topics = st.sidebar.multiselect(
    "📚 Choose Topics",
    ["World", "Politics", "Technology", "Science", "Health", "Business", "Entertainment", "Sports"],
    default=["World", "Technology", "Politics"]
)

# ------------------ HELPER FUNCTIONS ------------------

def get_news_headlines(query, max_results=5):
    headlines = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, region="wt-wt", safesearch="Moderate", timelimit="d"):
            if "title" in r and "href" in r:
                headlines.append(f"{r['title']} - {r['href']}")
            if len(headlines) >= max_results:
                break
    return headlines

def generate_topic_summary(headlines, topic, api_key):
    client = OpenAI(api_key=api_key)
    prompt = f"""You are a helpful news summarizer. Write a concise, informative, and engaging summary of the following {topic} news headlines:

{chr(10).join(headlines)}

Use bullet points if needed. Avoid repetition and focus on the main ideas."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

def export_summary_to_pdf(summaries_dict, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.cell(0, 10, f"📰 Daily News Summary - {date.strftime('%B %d, %Y')}", ln=True, align='C')
    pdf.ln(10)
    for topic, summary in summaries_dict.items():
        pdf.set_font("Arial", style='B', size=14)
        pdf.cell(0, 10, topic, ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, summary)
        pdf.ln()
    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

# ------------------ MAIN APP ------------------

if not openai_api_key:
    st.warning("Please enter your OpenAI API key in the sidebar.")
else:
    summaries = {}
    for topic in topics:
        st.markdown(f"## 🔎 {topic} News")
        headlines = get_news_headlines(f"{topic} news", max_results=num_articles)
        if headlines:
            for i, h in enumerate(headlines, 1):
                st.markdown(f"{i}. {h}")
            with st.spinner(f"Summarizing {topic}..."):
                summary = generate_topic_summary(headlines, topic, openai_api_key)
                st.markdown("### 📝 Summary")
                st.info(summary)
                summaries[topic] = summary
        else:
            st.warning(f"No headlines found for {topic}.")

    if summaries:
        pdf_file = export_summary_to_pdf(summaries, selected_date)
        st.download_button(
            label="📄 Download Full Summary PDF",
            data=pdf_file,
            file_name=f"categorized_news_{selected_date}.pdf",
            mime="application/pdf"
        )

st.caption("Created with ❤️ using DuckDuckGo, OpenAI, and Streamlit.")

