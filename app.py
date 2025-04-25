import streamlit as st
from duckduckgo_search import DDGS
import openai
import datetime

# ------------------ SETUP ------------------

st.set_page_config(page_title="Daily News Summary", layout="wide")

# Title
st.title("📰 Daily News Summary")

# Sidebar config
openai_api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
num_articles = st.sidebar.slider("Number of News Articles", 3, 15, 7)

# ------------------ FUNCTIONS ------------------

def get_news_headlines(query="daily news", max_results=7):
    headlines = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, region="wt-wt", safesearch="Moderate", timelimit="d"):
            if "title" in r and "href" in r:
                headlines.append(f"{r['title']} - {r['href']}")
            if len(headlines) >= max_results:
                break
    return headlines

def generate_summary(headlines, api_key):
    openai.api_key = api_key
    joined_headlines = "\n".join(headlines)
    prompt = f"""You are a helpful assistant. Summarize the following news headlines in a friendly, informative way, as if preparing a quick news brief:

{joined_headlines}

Make the summary concise and engaging."""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return response['choices'][0]['message']['content']

# ------------------ MAIN APP ------------------

if openai_api_key:
    st.subheader("Fetching Latest News Headlines...")
    headlines = get_news_headlines(max_results=num_articles)
    
    if headlines:
        st.success("News Headlines Retrieved Successfully!")
        st.write("### 🗞️ Top Headlines:")
        for i, headline in enumerate(headlines, 1):
            st.write(f"{i}. {headline}")

        st.write("### 🤖 Generating Summary...")
        summary = generate_summary(headlines, openai_api_key)
        st.markdown("### 📋 Summary Report")
        st.info(summary)
    else:
        st.warning("No news found. Try again later or adjust your query.")
else:
    st.warning("Please enter your OpenAI API key in the sidebar.")

# Footer
st.caption(f"Generated on {datetime.datetime.now().strftime('%B %d, %Y')}")
