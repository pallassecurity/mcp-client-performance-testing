import time
import os
import sys
import multiprocessing
from contextlib import contextmanager

from mcp.server.fastmcp import FastMCP


def run_server_silent(silent=True):
    """Module-level function that can be pickled."""
    if silent:
        # Redirect to devnull
        devnull = open(os.devnull, 'w')
        sys.stdout = devnull
        sys.stderr = devnull

    # Create the FastMCP instance inside the subprocess
    from mcp.server.fastmcp import FastMCP

    # Stateful server (maintains session state)
    # mcp = FastMCP("StatefulServer")

    # Other configuration options:
    # Stateless server (no session persistence)
    mcp = FastMCP("StatelessServer", stateless_http=True)

    # Stateless server (no session persistence, no sse stream with supported client)
    # mcp = FastMCP("StatelessServer", stateless_http=True, json_response=True)

    # Add a simple tool to demonstrate the server
    @mcp.tool()
    def greet(name: str = "World") -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    mcp.run(transport="streamable-http")


def run_server() -> None:
    """Run server normally (for direct execution)."""
    # Create the FastMCP instance
    mcp = FastMCP("StatelessServer", stateless_http=True)

    # Add a simple tool to demonstrate the server
    @mcp.tool()
    def greet(name: str = "World") -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"

    mcp.run(transport="streamable-http")


@contextmanager
def simple_mcp_server(silent=True, startup_sleep=2):
    ctx = multiprocessing.get_context('spawn')

    process = ctx.Process(target=run_server_silent, args=(silent,))
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