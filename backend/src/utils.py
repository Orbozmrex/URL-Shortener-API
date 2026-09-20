import secrets
from .config import Settings

async def generate_short_code(length: int = Settings.short_code_length):
    alphabet = Settings.short_code_alphabet
    return "".join(secrets.choice(alphabet) for _ in range(length))