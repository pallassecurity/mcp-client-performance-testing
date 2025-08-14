import asyncio
import webbrowser
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from mcp.client.auth import OAuthClientProvider
from mcp.shared.auth import OAuthClientMetadata
from pydantic import AnyUrl

from token_storage import InMemoryTokenStorage


class FastAPICallbackServer:
    def __init__(self, port=3000):
        self.port = port
        self.auth_code = None
        self.state = None
        self.received = None
        self.app = FastAPI()
        self.server = None
        self.server_task = None

        # Set up the route
        @self.app.get("/callback")
        async def handle_callback(request: Request):
            """Handle OAuth callback."""
            params = request.query_params
            self.auth_code = params.get('code')
            self.state = params.get('state')

            if self.received:
                self.received.set()

            return HTMLResponse(content="""
                <html>
                <body style="font-family: sans-serif; padding: 50px; text-align: center;">
                    <h1>✅ Authorization Successful!</h1>
                    <p>You can close this window and return to your application.</p>
                    <script>window.setTimeout(() => window.close(), 3000);</script>
                </body>
                </html>
            """)

    async def start(self):
        """Start the FastAPI server in the background."""
        print("Starting callback server...", end="")

        # Reset state for new session
        self.auth_code = None
        self.state = None
        self.received = asyncio.Event()

        config = uvicorn.Config(
            app=self.app,
            host="localhost",
            port=self.port,
            log_level="error"
        )
        self.server = uvicorn.Server(config)

        # Run server in background task
        self.server_task = asyncio.create_task(self.server.serve())

        # Wait a moment for server to start
        await asyncio.sleep(0.5)

        print(" done")

    async def stop(self):
        """Stop the server and wait for it to shut down."""
        print("Stopping callback server...", end="")

        if self.server:
            self.server.should_exit = True

            if self.server_task:
                try:
                    await asyncio.wait_for(self.server_task, timeout=5.0)
                except asyncio.TimeoutError:
                    print("Warning: Server did not stop within timeout")
                    self.server_task.cancel()
                    try:
                        await self.server_task
                    except asyncio.CancelledError:
                        pass

        self.received = None
        print(" done")

    async def wait_for_callback(self) -> tuple[str, str | None]:
        """Wait for OAuth callback."""
        if not self.received:
            raise RuntimeError("Server not started - call start() first")

        await self.received.wait()
        return self.auth_code, self.state

    def reset_for_new_auth(self):
        """Reset the server state for a new OAuth flow."""
        self.auth_code = None
        self.state = None
        self.received = asyncio.Event()


@asynccontextmanager
async def callback_server(port: int = 3000):
    """Context manager for the callback server."""
    server = FastAPICallbackServer(port=port)
    await server.start()

    try:
        yield server
    finally:
        await server.stop()


@asynccontextmanager
async def oauth_provider(server_url: str, callback_server_instance: FastAPICallbackServer):
    """Context manager for OAuth provider using an existing callback server."""

    # Reset the server for this OAuth flow
    callback_server_instance.reset_for_new_auth()

    async def redirect_handler(auth_url: str, print_url: bool = False) -> None:
        if print_url:
            print(f"Visit: {auth_url}")
        webbrowser.open(auth_url)
        print("Browser opened with auth URL")

    async def callback_handler() -> tuple[str, str | None]:
        return await callback_server_instance.wait_for_callback()

    auth = OAuthClientProvider(
        server_url=server_url,
        client_metadata=OAuthClientMetadata(
            client_name="Benchmark remote MCP client",
            redirect_uris=[AnyUrl(f"http://localhost:{callback_server_instance.port}/callback")],
            grant_types=["authorization_code", "refresh_token"],
            response_types=["code"],
            scope="user"
        ),
        storage=InMemoryTokenStorage(),
        redirect_handler=redirect_handler,
        callback_handler=callback_handler,
    )

    yield auth