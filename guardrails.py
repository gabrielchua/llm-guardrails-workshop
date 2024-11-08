def system_prompt_leakage(text: str, system_prompt: str) -> bool:
    """
    Check if the system prompt is leaked in the text.

    Parameters:
    - text: str - The text to check.
    - system_prompt: str - The system prompt to check against.

    Returns:
    - bool - True if the system prompt is leaked, False otherwise.
    """
    return text == system_prompt
