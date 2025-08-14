import asyncio
import time
from importlib.metadata import version
from typing import Coroutine, Any, Callable

import mcp
from httpx import Auth
from mcp import ClientSession
from mcp.client.auth import TokenStorage
from mcp.client.streamable_http import streamablehttp_client

from auth_provider import oauth_provider, callback_server, FastAPICallbackServer
from simple_mcp_server import simple_mcp_server
from token_storage import InMemoryTokenStorage


async def test_connect_client_for_simple() -> float:
    start = time.perf_counter()
    async with streamablehttp_client("http://localhost:8000/mcp") as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            end = time.perf_counter()

            test_result = end - start

            list_result = await session.list_tools()
            assert len(list_result.tools) == 1

    return test_result


async def test_list_tools_simple() -> float:
    async with streamablehttp_client("http://localhost:8000/mcp") as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            start = time.perf_counter()

            list_result = await session.list_tools()

            end = time.perf_counter()

            test_result = end - start

            assert len(list_result.tools) == 1

    return test_result


async def test_call_tool_simple() -> float:
    async with streamablehttp_client("http://localhost:8000/mcp") as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            start = time.perf_counter()

            call_tool_result = await session.call_tool("greet", {"name": "Josh"})

            end = time.perf_counter()

            test_result = end - start

            assert call_tool_result.content[0].text == "Hello, Josh!"

    return test_result


async def test_notion_connection(auth: Auth) -> float:
    start = time.perf_counter()
    async with streamablehttp_client("https://mcp.notion.com/mcp", auth=auth) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            end = time.perf_counter()
            test_result = end - start

            tools_response = await session.list_tools()
            assert len(tools_response.tools) > 0

    return test_result


async def test_oauth_provider_construction(cb_server: FastAPICallbackServer, token_storage: TokenStorage) -> float:
    start = time.perf_counter()
    async with oauth_provider("https://mcp.notion.com/mcp", cb_server, token_storage) as _:
        end = time.perf_counter()
        test_result = end - start

    return test_result


async def test_list_tools(session: ClientSession) -> float:
    start = time.perf_counter()
    tools_response = await session.list_tools()
    end = time.perf_counter()
    test_result = end - start
    assert len(tools_response.tools) > 0
    return test_result


async def test_call_tool(session: ClientSession, tool_name: str, arguments: dict) -> float:
    start = time.perf_counter()
    call_response = await session.call_tool(tool_name, arguments)
    end = time.perf_counter()
    test_result = end - start
    assert len(call_response.content) > 0
    return test_result


async def test_github_connection(pat: str) -> float:
    headers = {
        "Authorization": f"Bearer {pat}",
    }
    start = time.perf_counter()
    async with streamablehttp_client("https://api.githubcopilot.com/mcp/", headers=headers) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            end = time.perf_counter()
            test_result = end - start

            tools_response = await session.list_tools()
            assert len(tools_response.tools) > 0

    return test_result


N_TRIALS = 5


async def repeat_tests(test: Callable[[], Coroutine[Any, Any, float]]) -> None:
    print("Test results:", end="")
    results = []
    for _ in range(N_TRIALS):
        result = await test()
        print(f" {result:.04f}", end="")
        results.append(result)
    print(f" (avg {sum(results) / N_TRIALS:.04f}s)")


async def main() -> None:
    print(f"Starting tests with official Python MCP SDK version {version('mcp')}")
    print()

    with simple_mcp_server() as _:
        print("Running simple client connection tests...")
        await repeat_tests(test_connect_client_for_simple)
        print()

        print("Running simple tool list tests...")
        await repeat_tests(test_list_tools_simple)
        print()

        print("Running simple tool call tests...")
        await repeat_tests(test_call_tool_simple)
        print()

    async with callback_server() as cb_server:

        notion_token_storage = InMemoryTokenStorage()
        print("Running in memory OAuth provider construction tests...")
        await repeat_tests(lambda: test_oauth_provider_construction(cb_server, notion_token_storage))
        print()

        async with oauth_provider("https://mcp.notion.com/mcp", cb_server, notion_token_storage) as notion_auth:
            print("Running Notion client connection tests (OAuth)...")
            await repeat_tests(lambda: test_notion_connection(notion_auth))
            print()

            async with streamablehttp_client("https://mcp.notion.com/mcp", auth=notion_auth) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as notion_session:
                    await notion_session.initialize()

                    print("Running Notion list tools tests...")
                    await repeat_tests(lambda: test_list_tools(notion_session))
                    print()

                    print("Running Notion call tool tests...")
                    await repeat_tests(lambda: test_call_tool(notion_session, "notion-get-self", {}))
                    print()

    github_pat = ""

    print("Running GitHub client connection tests (PAT)...")
    await repeat_tests(lambda: test_github_connection(github_pat))
    print()

    headers = {
        "Authorization": f"Bearer {github_pat}",
    }
    async with streamablehttp_client("https://api.githubcopilot.com/mcp/", headers=headers) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as github_session:
            await github_session.initialize()

            print("Running GitHub list tools tests...")
            await repeat_tests(lambda: test_list_tools(github_session))
            print()

            print("Running GitHub call tool tests...")
            await repeat_tests(lambda: test_call_tool(github_session, "get_me", {}))
            print()

    print("Finished!")


if __name__ == "__main__":
    asyncio.run(main())
