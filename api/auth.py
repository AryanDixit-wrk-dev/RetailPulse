import os
import secrets

from dotenv import load_dotenv
from fastapi import Header, HTTPException


load_dotenv()


def verify_api_key(
    x_api_key: str | None = Header(default=None),
):
    expected_api_key = os.getenv("API_KEY")

    if not expected_api_key:
        raise HTTPException(
            status_code=500,
            detail="API authentication is not configured.",
        )

    if x_api_key is None or not secrets.compare_digest(
        x_api_key,
        expected_api_key,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
        )

    return x_api_key