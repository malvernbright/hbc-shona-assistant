"""Package for hbc_shona_assistant."""

# Simple entrypoint used by uv when building the package.

def main() -> None:
    """Minimal main function.
    Prints a welcome message.
    """
    print("Hello from hbc_shona_assistant package!")

# Re-export key modules for convenience.
from . import main as main_module  # type: ignore
