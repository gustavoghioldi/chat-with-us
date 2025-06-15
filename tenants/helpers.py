import secrets
import string


def generate_cwu_token():
    """Generate a random alphanumeric token of 36 characters starting with 'cwu_'."""
    characters = string.ascii_letters + string.digits
    random_part = "".join(secrets.choice(characters) for _ in range(32))
    return f"cwu_{random_part}"
