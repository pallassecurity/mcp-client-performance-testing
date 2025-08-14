import time
import multiprocessing
from contextlib import contextmanager

from mcp.server.fastmcp import FastMCP


def run_server():
    mcp = FastMCP("StatelessServer", stateless_http=True, log_level="ERROR")

    # Add a simple tool to demonstrate the server
    @mcp.tool()
    def greet(name: str = "World") -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    mcp.run(transport="streamable-http")


@contextmanager
def simple_mcp_server(startup_sleep=2):
    ctx = multiprocessing.get_context('spawn')

    process = ctx.Process(target=run_server)
    process.daemon = True
    process.start()

    time.sleep(startup_sleep)

    try:
        yield process
    finally:
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
            if process.is_alive():
                process.kill()
                process.join()


# Run server with streamable_http transport
if __name__ == "__main__":
    run_server()