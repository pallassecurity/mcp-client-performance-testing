import asyncio
import time
from typing import Coroutine, Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from sample_server import simple_mcp_server


async def test_connect_client_for_simple() -> float:
    with simple_mcp_server() as _:
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
    with simple_mcp_server() as _:
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
    with simple_mcp_server() as _:
        async with streamablehttp_client("http://localhost:8000/mcp") as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                start = time.perf_counter()

                call_tool_result = await session.call_tool("greet", {"name": "Josh"})

                end = time.perf_counter()

                test_result = end - start

                assert call_tool_result.content[0].text == "Hello, Josh!"

    return test_result


N_TRIALS = 5


async def repeat_tests(test: Coroutine[Any, Any, float]) -> None:
    results = [await test() for _ in range(N_TRIALS)]
    formatted_results = [f"{result:0.4f}s" for result in results]
    print(f"Test results: {formatted_results} (avg {sum(results) / N_TRIALS:.04f}s)")


async def main() -> None:
    print("Running simple client connection tests...")
    await repeat_tests(test_connect_client_for_simple)

    print("Running simple tool list tests...")
    await repeat_tests(test_list_tools_simple)

    print("Running simple tool call tests...")
    await repeat_tests(test_call_tool_simple)


if __name__ == "__main__":
    asyncio.run(main())
