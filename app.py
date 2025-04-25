import streamlit as st
from duckduckgo_search import DDGS
from openai import OpenAI
from fpdf import FPDF
import datetime
import io

# ------------------ CONFIG ------------------
st.set_page_config(page_title="📰 Daily News Summary", layout="wide")
st.title("🗞️ Daily News Summary App")

# Sidebar inputs
openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
num_articles = st.sidebar.slider("Number of News Articles", 3, 15, 7)
selected_date = st.sidebar.date_input("Select Date for News", datetime.date.today())

# ------------------ HELPER FUNCTIONS ------------------

def get_news_headlines(query="daily news", max_results=7, date=None):
    headlines = []
    with DDGS() as ddgs:
        timelimit = "d" if date == datetime.date.today() else None  # DDG supports only limited time filters
        for r in ddgs.text(query, region="wt-wt", safesearch="Moderate", timelimit=timelimit):
            if "title" in r and "href" in r:
                headlines.append(f"{r['title']} - {r['href']}")
            if len(headlines) >= max_results:
                break
    return headlines

def generate_summary(headlines, api_key):
    client = OpenAI(api_key=api_key)
    joined_headlines = "\n".join(headlines)

    prompt = f"""
You are a helpful assistant. Summarize the following news headlines into a concise and informative daily news brief:

{joined_headlines}

Make the summary clear and engaging.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=600
    )

    return response.choices[0].message.content

def export_summary_to_pdf(summary_text, date):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"📰 Daily News Summary - {date.strftime('%B %d, %Y')}\n\n{summary_text}")
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# ------------------ MAIN APP ------------------

if openai_api_key:
    st.subheader(f"Fetching News for {selected_date.strftime('%B %d, %Y')}...")

    headlines = get_news_headlines(max_results=num_articles, date=selected_date)

    if headlines:
        st.success("Headlines Retrieved!")
        st.write("### 🔗 Headlines:")
        for i, headline in enumerate(headlines, 1):
            st.write(f"{i}. {headline}")

        st.write("### 🤖 Generating Summary...")
        summary = generate_summary(headlines, openai_api_key)
        st.markdown("### 📋 Summary Report")
        st.info(summary)

        # PDF Export Button
        pdf_file = export_summary_to_pdf(summary, selected_date)
        st.download_button(
            label="📄 Download Summary as PDF",
            data=pdf_file,
            file_name=f"news_summary_{selected_date}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("No news found for that date or query.")
else:
    st.warning("Please enter your OpenAI API key in the sidebar.")

st.caption("Created with ❤️ using DuckDuckGo, OpenAI, and Streamlit.")

