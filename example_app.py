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
from guardrails import openai_moderation, sentinel

if check_secrets():
    st.error("Please set the required environment variables.")
    st.stop()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

THRESHOLD_LG = 0.5
THRESHOLD_PG = 0.5
THRESHOLD_OT = 0.5

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
            if input_guardrail(job_description, resume):
                st.warning("Please revise your inputs.")
            else:
                # Only continue if _score is less than threshold
                st.divider()
                st.subheader("Your Cover Letter")
                cover_letter_box = st.empty()
                generate_cover_letter(
                    job_description, resume, style, additional_info, cover_letter_box
                )


def input_guardrail(job_description: str, resume: str) -> bool:
    """
    Parameters:
    - job_description (str): The text of the job description to validate.
    - resume (str): The text of the resume to validate.

    Returns:
    - bool: `True` if either input fails any of the guardrails, otherwise `False`.
    """
    # Perform moderation checks
    jd_moderation = openai_moderation(text=job_description)
    r_moderation = openai_moderation(text=resume)

    # Apply sentinel filters
    jd_response = sentinel(
        text=job_description, filters=["lionguard", "promptguard"], detail="scores"
    )
    resume_response = sentinel(
        text=resume, filters=["lionguard", "promptguard"], detail="scores"
    )

    # Extract scores for job description
    jd_lg_binary_score = jd_response["lionguard"]["binary"]["score"]
    jd_pg_score = jd_response["promptguard"]["jailbreak"]

    # Extract scores for resume
    r_lg_binary_score = resume_response["lionguard"]["binary"]["score"]
    r_pg_score = resume_response["promptguard"]["jailbreak"]

    # Evaluate conditions
    if jd_moderation or r_moderation:
        return True
    st.toast("Passed OpenAI Moderation")
    if jd_lg_binary_score > THRESHOLD_LG or r_lg_binary_score > THRESHOLD_LG:
        return True
    st.toast("Pass LionGuard check")
    if jd_pg_score > THRESHOLD_PG or r_pg_score > THRESHOLD_PG:
        return True
    st.toast("Pass PromptGuard check")
    return False


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

    resume_ot_response = sentinel(
        text=job_description,
        filters=["off-topic"],
        system_prompt=system_prompt,
    )["off-topic"]["off-topic"]

    jd_ot_response = sentinel(
        text=resume,
        filters=["off-topic"],
        system_prompt=system_prompt,
    )["off-topic"]["off-topic"]

    if resume_ot_response > THRESHOLD_OT or jd_ot_response > THRESHOLD_OT:
        st.warning("Please revise your inputs.")
        st.stop()
    st.toast("Passed off-topic check")

    stream = client.chat.completions.create(
        model="gpt-4o",
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
