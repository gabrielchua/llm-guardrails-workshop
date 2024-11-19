"""
utils.py
"""

import os


def check_secrets():
    """
    Check if the setup is correct.
    """
    required_secrets = ["OPENAI_API_KEY", "SENTINEL_API_ENDPOINT", "SENTINEL_API_KEY"]
    missing_secrets = [secret for secret in required_secrets if not os.getenv(secret)]

    if missing_secrets:
        return True
