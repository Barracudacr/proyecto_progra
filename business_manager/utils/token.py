from pathlib import Path

TOKEN_FILE = Path("token.txt")


def save_token(token: str):
    TOKEN_FILE.write_text(token)
    
    
def get_token():
    if not TOKEN_FILE.exists():
        return None
    return TOKEN_FILE.read_text().strip()