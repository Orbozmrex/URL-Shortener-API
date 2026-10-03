import secrets
from .config import Settings
import qrcode
import io

async def generate_short_code(length: int = Settings.short_code_length):
    alphabet = Settings.short_code_alphabet
    return "".join(secrets.choice(alphabet) for _ in range(length))

async def generate_qr_code(short_code):
    img = qrcode.make(f"https://{Settings.domain}/{short_code}")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer