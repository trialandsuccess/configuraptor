"""
Contains stand-alone helper functions.
"""


def camel_to_snake(s: str) -> str:
    """
    Convert CamelCase to snake_case.

    Source:
        https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    return "".join([f"_{c.lower()}" if c.isupper() else c for c in s]).lstrip("_")
