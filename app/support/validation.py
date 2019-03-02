from typing import Callable


def validate_arg(expr: bool, msg: str) -> None:
    """
    Validates an argument.
    :param expr: The validation expression, which must be true.
    :param msg:  The message for the `ValueError` to raise if `expr` fails.
    :raises ValueError: If validation fails, an explanation why.
    """
    if not expr:
        raise ValueError(msg)


def validate_data(expr: bool, error: Callable[[], Exception]) -> None:
    """
    Validates data.
    :param expr:  The validation expression, which must be true.
    :param error: A callable that will raise an error if `expr` fails.
    :raises Exception: If validation fails, an explanation why.
    """
    if not expr:
        raise error()
