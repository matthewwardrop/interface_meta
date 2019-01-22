import logging


def report_violation(message, raise_on_violation):
    if raise_on_violation:
        raise RuntimeError(message)
    else:
        logging.warning(message)
