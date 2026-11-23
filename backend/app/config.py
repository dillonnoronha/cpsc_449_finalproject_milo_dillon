"""Browser origins allowed to call the API from a separate site."""
import os


def frontend_origins() -> list[str]:
    return [
        value.strip().rstrip("/")
        for value in os.environ.get("FRONTEND_ORIGINS", "").split(",")
        if value.strip()
    ]
