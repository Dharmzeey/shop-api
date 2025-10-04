import logging

logger = logging.getLogger('custom_logger')

def log_error(error_message, exception=None):
    if exception:
        logger.error(f"{error_message} - Exception: {exception}", exc_info=True)
    else:
        logger.error(error_message)
