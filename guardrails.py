"""
guardrails.py

This module contains the guardrail functions

- `sentinel`: Check text using the Sentinel API for various guardrails.
- `sentinel_async`: Async version of `sentinel`.
- `system_prompt_leakage`: Check if the system prompt is leaked in the text.
- `grounding_check`: Check if the text is grounded in the context.

"""
# Standard Library
import os
from typing import TypedDict, Literal

# Third Party
import aiohttp
import requests
from openai import OpenAI

# Load the secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SENTINEL_API_ENDPOINT = os.getenv("SENTINEL_API_ENDPOINT")
SENTINEL_API_KEY = os.getenv("SENTINEL_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def openai_moderation(text: str) -> bool:
    """
    Check text using OpenAI's Moderation Endpoint

    Parameters:
    - text: str - The text to check

    Returns:
    - 
    """
    response = client.moderations.create(
        model="omni-moderation-latest",
        input=text
    )

    return response.results[0].flagged



def sentinel(
    text: str,
    filters: list[str],
    system_prompt: str | None = None,
    detail: str | None = None,
    score_selection: str | None = None
) -> dict:
    """
    Check text using the Sentinel API for various guardrails.

    Parameters:
    - text: str - The text to check
    - filters: list[str] - List of filters to apply
    - system_prompt: str | None - Required system prompt for off-topic/off-topic-2 filters
    - detail: str | None - Detail level for lionguard filter ("predictions" or "scores")
    - score_selection: str | None - Score selection mode for lionguard ("balanced", "high_precision", or "high_recall")

    Returns:
    - dict - Response from Sentinel API containing filter results
    """
    if SENTINEL_API_ENDPOINT is None:
        raise ValueError("SENTINEL_API_ENDPOINT environment variable is not set")
        
    headers = {
        "x-api-key": SENTINEL_API_KEY,
        "Content-Type": "application/json"
    }

    params = {}
    
    # Add params for off-topic filters if needed
    if "off-topic" in filters and system_prompt:
        params["off-topic"] = {"system_prompt": system_prompt}
    if "off-topic-2" in filters and system_prompt:
        params["off-topic-2"] = {"system_prompt": system_prompt}
        
    # Add params for lionguard if needed
    if "lionguard" in filters and score_selection:
        params["lionguard"] = {"score_selection": score_selection}

    payload = {
        "filters": filters,
        "text": text,
        "params": params
    }

    # Add detail level if specified
    if detail:
        payload["detail"] = detail

    response = requests.post(
        url=SENTINEL_API_ENDPOINT,
        headers=headers,
        json=payload,
        timeout=30
    )

    return response.json()["outputs"]

async def sentinel_async(
    text: str,
    filters: list[str],
    system_prompt: str | None = None,
    detail: str | None = None,
    score_selection: str | None = None
) -> dict:
    """
    Async version of `sentinel`.
    
    Parameters:
    - text: str - The text to check
    - filters: list[str] - List of filters to apply
    - system_prompt: str | None - Required system prompt for off-topic/off-topic-2 filters
    - detail: str | None - Detail level for lionguard filter ("predictions" or "scores")
    - score_selection: str | None - Score selection mode for lionguard ("balanced", "high_precision", or "high_recall")

    Returns:
    - dict - Response from Sentinel API containing filter results
    """
    if SENTINEL_API_ENDPOINT is None:
        raise ValueError("SENTINEL_API_ENDPOINT environment variable is not set")
        
    headers = {
        "x-api-key": SENTINEL_API_KEY,
        "Content-Type": "application/json"
    }

    params: SentinelParams = {}
    
    # Add params for off-topic filters if needed
    if "off-topic" in filters and system_prompt:
        params["off-topic"] = {"system_prompt": system_prompt}
    if "off-topic-2" in filters and system_prompt:
        params["off-topic-2"] = {"system_prompt": system_prompt}
        
    # Add params for lionguard if needed
    if "lionguard" in filters and score_selection:
        params["lionguard"] = {"score_selection": score_selection}

    payload = {
        "filters": filters,
        "text": text,
        "params": params
    }

    # Add detail level if specified
    if detail:
        payload["detail"] = detail

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=SENTINEL_API_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        ) as response:
            return await response.json()

################################################################################
# Output Guardrails
################################################################################

def system_prompt_leakage(text: str, system_prompt: str) -> bool:
    """
    Check if the system prompt is leaked in the text.

    Parameters:
    - text: str - The text to check.
    - system_prompt: str - The system prompt to check against.

    Returns:
    - bool - True if the system prompt is leaked, False otherwise.
    """
    # Split the system prompt and text into words, converting both to lowercase for case-insensitive matching
    system_words = set(system_prompt.lower().split())
    text_words = set(text.lower().split())
    
    # Calculate the number of words in the system prompt that are present in the text
    common_words = system_words.intersection(text_words)
    
    # Check if at least 95% of the system prompt words are in the text
    if len(common_words) / len(system_words) >= 0.95:
        return True
    return False    


def grounding_check(text: str, context: str) -> bool:
    """
    Check if the text is grounded in the context.

    Parameters:
    - text: str - The text to check.
    - context: str - The context to check against.

    Returns:
    - bool - True if the text is grounded in the context, False otherwise.
    """
    SYSTEM_PROMPT = """
        Your task is to determine if the text is grounded in the context.
        You will be given a text and a context.
        You will then output a 0 if the text is not grounded in the context, and a 1 if it is.
    """.strip()

    USER_PROMPT = """
        <context>
        {context}
        </context>

        <text>
        {text}
        </text>
    """.strip()

    return _zero_shot_classifier(SYSTEM_PROMPT, USER_PROMPT)


def _zero_shot_classifier(system_prompt: str, user_prompt: str) -> bool:
    """
    Get a chat completion from the OpenAI API.

    Parameters:
    - system_prompt: str - The system prompt defining the zero-shot classification task.
    - user_prompt: str - The text classify.

    Returns:
    - int - The predicted label (0 or 1).
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}],
        temperature=0,
        seed=0,
        max_tokens=1,
        logit_bias={
            "15": 100, # Token ID for `0`
            "16": 100 # Token ID for `1`
        }
    )
    return bool(response.choices[0].message.content)
