import asyncio
import time
from typing import Coroutine, Any, Callable

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from auth_provider import oauth_provider, callback_server
from simple_mcp_server import simple_mcp_server
from util import with_process


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


async def test_notion_connection(auth) -> float:
    start = time.perf_counter()
    async with streamablehttp_client("https://mcp.notion.com/mcp", auth=auth) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            end = time.perf_counter()
            test_result = end - start

            tools_response = await session.list_tools()
            assert len(tools_response.tools) > 0

    return test_result


async def test_oauth_provider_construction(cb_server) -> float:
    start = time.perf_counter()
    async with oauth_provider("https://mcp.notion.com/mcp", cb_server) as _:
        end = time.perf_counter()
        test_result = end - start

    return test_result


N_TRIALS = 5


async def repeat_tests(test: Callable[[], Coroutine[Any, Any, float]]) -> None:
    results = [await test() for _ in range(N_TRIALS)]
    formatted_results = [f"{result:0.4f}s" for result in results]
    print(f"Test results: {formatted_results} (avg {sum(results) / N_TRIALS:.04f}s)")


async def main() -> None:
    with simple_mcp_server() as _:
        print("Running simple client connection tests...")
        await repeat_tests(test_connect_client_for_simple)

        print("Running simple tool list tests...")
        await repeat_tests(test_list_tools_simple)

        print("Running simple tool call tests...")
        await repeat_tests(test_call_tool_simple)

    async with callback_server() as cb_server:
        print("Running in memory OAuth provider construction tests...")
        await repeat_tests(lambda: test_oauth_provider_construction(cb_server))

        async with oauth_provider("https://mcp.notion.com/mcp", cb_server) as auth:
            print("Running Notion client connection tests...")
            await repeat_tests(lambda: test_notion_connection(auth))


if __name__ == "__main__":
    asyncio.run(main())
