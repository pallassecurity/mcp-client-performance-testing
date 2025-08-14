import multiprocessing
import time
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
