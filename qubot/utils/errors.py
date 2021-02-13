from typing import Callable, Optional

from time import sleep

def inline_try(func: Callable) -> Optional[Exception]:
    """
    Try to execute an inline function without throwing an error. Useful when the Exception thrown is trivial.
    :param func: A function to call.
    :return: None if no exception is thrown or the Exception object thrown.
    """
    try:
        func()
        return None
    except Exception as e:
        return e

def try_again_on_fail(func: Callable, sleep_s: int = 0, max_retries: int = 0):
    """
    Recursively tries to execute the inline function until it succeeds.
    :param func: A function to call.
    :param sleep_s: Number of seconds to sleep before trying again.
    :param max_retries: The max number of retries before we finally propagate the error.
    """
    try:
        func()
    except Exception as e:
        if sleep_s > 0:
            sleep(sleep_s)
        if max_retries > 0:
            try_again_on_fail(func, sleep_s, max_retries - 1)
        else:
            raise e
