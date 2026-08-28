import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """All configuration is read from environment variables.
    Nothing here is ever hard-coded so secrets never end up committed.
    """

    cognodb_uri: str = os.environ.get("COGNODB_URI", "")
    cognodb_user: str = os.environ.get("COGNODB_USER", "cognodb")
    cognodb_password: str = os.environ.get("COGNODB_PASSWORD", "")

    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")

    cors_origins: list[str] = [
        o.strip()
        for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
        if o.strip()
    ]

    def validate(self) -> list[str]:
        """Return a list of human-readable problems with the current config."""
        problems = []
        if not self.cognodb_uri:
            problems.append("COGNODB_URI is not set")
        if not self.cognodb_password:
            problems.append("COGNODB_PASSWORD is not set")
        if not self.anthropic_api_key:
            problems.append("ANTHROPIC_API_KEY is not set")
        return problems


settings = Settings()
