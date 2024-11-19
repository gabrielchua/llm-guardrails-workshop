"""
app.py
"""

# Standard library imports
import os
import random

# Third-party imports
import streamlit as st
from openai import OpenAI

# Local imports
from utils import check_secrets
from samples import articles

# Check if the setup is correct
if check_secrets():
    st.error("⚠️ Please ensure all required secrets are set.")
    st.stop()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("📰 News Summarizer App")

    news_article = st.text_area(
        "Enter the news article here:",
        height=300,
        value=st.session_state.get("placeholder_news_article", ""),
    )
    random_article = st.button("🔄 Random Article")
    style = st.text_input(
        "(Optional) What style (e.g., tone, length) would you like the summary to be in?"
    )
    summarize_btn = st.button("📝 Summarise")

    if random_article:
        news_article = random.choice(articles)
        # Keep picking a random article until it's not the same as the one we already have
        while news_article == st.session_state.get("placeholder_news_article"):
            news_article = random.choice(articles)
        st.session_state["placeholder_news_article"] = news_article
        st.rerun()

    if summarize_btn and news_article:
        st.spinner("Summarising the news article...")
        summary = summarize_news(news_article, style)
        st.divider()
        st.subheader("Summary")
        st.info(summary)


def summarize_news(news_article: str, style: str) -> str | None:
    """
    Summarise the news article.

    Parameters:
    - news_article (str): The news article to summarise.

    Returns:
    - str: The summary of the news article.
    """

    system_prompt = f"""
    Please summarise the following news article.
    {"Use this style: " + style if style else ""}
    """.strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": news_article[:500]},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    main()
