import functools
import multiprocessing
import time
import types
from contextlib import contextmanager
from typing import Callable


@contextmanager
def with_process(target: Callable, args: tuple | None = None, startup_sleep: int | None = None, join_timeout: int = 5):
    ctx = multiprocessing.get_context('spawn')

    process = ctx.Process(target=target, args=args or tuple())
    process.daemon = True
    process.start()

    if startup_sleep:
        time.sleep(startup_sleep)

    try:
        yield process
    finally:
        if process.is_alive():
            process.terminate()
            process.join(timeout=join_timeout)
            if process.is_alive():
                process.kill()
                process.join()


def time_method(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = method(*args, **kwargs)
        end = time.perf_counter()
        print(f"{method.__qualname__} took {end - start:.6f} seconds")
        return result
    return wrapper


def profile_methods(cls):
    for name, attr in cls.__dict__.items():
        if isinstance(attr, types.FunctionType):
            def make_wrapper(func):
                def wrapper(*args, **kwargs):
                    start = time.perf_counter()
                    result = func(*args, **kwargs)
                    end = time.perf_counter()
                    elapsed = end - start
                    print(f"{cls.__name__}.{func.__name__} took {elapsed:.6f} seconds")
                    return result
                return wrapper
            setattr(cls, name, make_wrapper(attr))
    return cls
