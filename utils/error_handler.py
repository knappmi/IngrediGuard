import functools
# Attempt to import Kivy's logger, but create a dummy if it fails.
# This allows any decorated module to be tested without a Kivy environment.
try:
    from kivy.logger import Logger
except ImportError:
    import logging
    Logger = logging.getLogger(__name__)
    Logger.info = Logger.debug
    Logger.warning = Logger.warning
    Logger.error = Logger.error
    Logger.critical = Logger.critical

def error_handler(func):
    """
    Decorator for handling errors in functions.
    Logs errors to the application logger.
    
    Usage:
        @error_handler
        def my_function():
            # Your code here
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Log function call
            if args:
                Logger.info(f"Calling {func.__name__} on {type(args[0]).__name__}")
            if kwargs:
                Logger.info(f"Arguments: {kwargs}")
            
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error
            Logger.error(f"Error in {func.__name__}: {str(e)}")
            Logger.error(f"Error type: {type(e).__name__}")
            
            # Re-raise the exception
            raise
    return wrapper