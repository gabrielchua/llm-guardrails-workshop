"""
app.py - Cover Letter Generator
"""

# Standard library imports
import os
import random

# Third-party imports
import streamlit as st
from openai import OpenAI

# Local imports
from samples import resumes, job_descriptions
from utils import check_secrets

if check_secrets():
    st.error("Please set the required environment variables.")
    st.stop()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def main():
    """
    Main function to run the Cover Letter Generator app.
    """
    st.title("✍️ Cover Letter Generator")

    # Input fields
    job_description = st.text_area(
        "Enter the job description:",
        height=200,
        placeholder="Paste the job description here...",
        value=st.session_state.get("job_description", ""),
    )

    resume = st.text_area(
        "Enter your resume:",
        height=200,
        placeholder="Paste your resume or key experiences here...",
        value=st.session_state.get("resume", ""),
    )

    style = st.text_input(
        "Writing Style (Optional)",
        placeholder="e.g., professional, enthusiastic, concise",
    )

    additional_info = st.text_area(
        "Additional Information (Optional):",
        height=100,
        placeholder="Any specific points you'd like to emphasize or company-specific details...",
    )

    # Load example button
    load_example = st.button("📋 Load Examples")
    if load_example:
        example_job = random.choice(job_descriptions)
        example_resume = random.choice(resumes)
        st.session_state["job_description"] = example_job
        st.session_state["resume"] = example_resume
        st.rerun()

    generate_btn = st.button("📝 Generate Cover Letter")

    if generate_btn and job_description and resume:
        with st.spinner("Generating your cover letter..."):
            st.divider()
            st.subheader("Your Cover Letter")
            cover_letter_box = st.empty()
            generate_cover_letter(
                job_description, resume, style, additional_info, cover_letter_box
            )


def generate_cover_letter(
    job_description: str, resume: str, style: str, additional_info: str, text_box
) -> None:
    """
    Generate a cover letter based on the job description and resume.

    Parameters:
    - job_description (str): The job posting description
    - resume (str): The applicant's resume or relevant experiences
    - style (str): Preferred writing style
    - additional_info (str): Any additional information to consider

    Returns:
    - str: The generated cover letter
    """

    system_prompt = f"""
    You will receive:
    - A Job Description
    - A Resume
    - (Optionally) Additional Information
    
    Please write a cover letter based on above info.

    Style: {style if style else 'professional tone'}
    """.strip()

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Job Description:\n{job_description}\n\nResume:\n{resume}\n\nAdditional Information:\n{additional_info}",
            },
        ],
        stream=True,
    )
    text = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            text += chunk.choices[0].delta.content
            text_box.empty()
            text_box.info(text)


if __name__ == "__main__":
    main()
