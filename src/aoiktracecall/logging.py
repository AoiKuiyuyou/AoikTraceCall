# coding: utf-8
from __future__ import absolute_import

# Standard imports
import logging


# Debug logger.
# Initialized in `get_debug_logger`.
_DEBUG_LOGGER = None

# Info logger.
# Initialized in `get_info_logger`.
_INFO_LOGGER = None

# Error logger.
# Initialized in `get_error_logger`.
_ERROR_LOGGER = None


def set_debug_logger(logger):
    # Use global
    global _DEBUG_LOGGER

    # Set logger
    _DEBUG_LOGGER = logger


def get_debug_logger():
    # Use global
    global _DEBUG_LOGGER

    # If logger is not initialized
    if _DEBUG_LOGGER is None:
        # Get logger
        _DEBUG_LOGGER = logging.getLogger(
            'aoiktracecall.logging.DEBUG_LOGGER'
        )

        # Disable propagation
        _DEBUG_LOGGER.propagate = False

        # Set logging level
        _DEBUG_LOGGER.setLevel(logging.DEBUG)

    # Return logger
    return _DEBUG_LOGGER


def set_info_logger(logger):
    # Use global
    global _INFO_LOGGER

    # Set logger
    _INFO_LOGGER = logger


def get_info_logger():
    # Use global
    global _INFO_LOGGER

    # If logger is not initialized
    if _INFO_LOGGER is None:
        # Get logger
        _INFO_LOGGER = logging.getLogger(
            'aoiktracecall.logging.INFO_LOGGER'
        )

        # Disable propagation
        _INFO_LOGGER.propagate = False

        # Set logging level
        _INFO_LOGGER.setLevel(logging.INFO)

    # Return logger
    return _INFO_LOGGER


def set_error_logger(logger):
    # Use global
    global _ERROR_LOGGER

    # Set logger
    _ERROR_LOGGER = logger


def get_error_logger():
    # Use global
    global _ERROR_LOGGER

    # If logger is not initialized
    if _ERROR_LOGGER is None:
        # Get logger
        _ERROR_LOGGER = logging.getLogger(
            'aoiktracecall.logging.ERROR_LOGGER'
        )

        # Disable propagation
        _ERROR_LOGGER.propagate = False

        # Set logging level
        _ERROR_LOGGER.setLevel(logging.INFO)

    # Return logger
    return _ERROR_LOGGER


def print_debug(text):
    # If have text
    if text:
        # Get logger
        logger = get_debug_logger()

        # Send text to logger
        logger.debug(text)


def print_info(text):
    # If have text
    if text:
        # Get logger
        logger = get_info_logger()

        # Send text to logger
        logger.info(text)


def print_error(text):
    # If have text
    if text:
        # Get logger
        logger = get_error_logger()

        # Send text to logger
        logger.error(text)
