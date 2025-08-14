# MCP Client Performance Testing

The purpose of this repository is to test the performance of the MCP client in the Model Context Protocol official
Python SDK. We have experienced some issues with performance, particularly the
`mcp.client.streamable_http.streamablehttp_client` and `mcp.client.auth.OAuthClientProvider`. 

These issues are present when using the Notion remote MCP server with OAuth.

# Test Results

## SDK Version 1.11.0 (latest without bug)

```
Starting tests with official Python MCP SDK version 1.11.0

Running simple client connection tests...
Test results: 0.0614 0.0136 0.0120 0.0116 0.0106 (avg 0.0219s)

Running simple tool list tests...
Test results: 0.0042 0.0041 0.0041 0.0041 0.0047 (avg 0.0042s)

Running simple tool call tests...
Test results: 0.0080 0.0067 0.0068 0.0072 0.0246 (avg 0.0107s)

Starting callback server... done
Running in memory OAuth provider construction tests...
Test results: 0.0016 0.0001 0.0000 0.0000 0.0000 (avg 0.0004s)

Running Notion client connection tests (OAuth)...
Test results: 6.0797 0.9399 0.9005 0.8184 1.0262 (avg 1.9529s)

Running Notion list tools tests...
Test results: 0.3850 0.1293 0.1308 0.1496 0.1233 (avg 0.1836s)

Running Notion call tool tests...
Test results: 0.4083 0.6162 0.8519 0.1946 0.6942 (avg 0.5530s)

Stopping callback server... done
Running GitHub client connection tests (PAT)...
Test results: 0.5784 0.2820 0.2962 0.2857 0.3079 (avg 0.3500s)

Running GitHub list tools tests...
Test results: 0.5216 0.1121 0.1129 0.1286 0.1175 (avg 0.1986s)

Running GitHub call tool tests...
Test results: 0.2627 0.3505 0.2029 0.2623 0.3536 (avg 0.2864s)

Finished!
```

## SDK Version 1.12.1 (earliest with bug)

```
Starting tests with official Python MCP SDK version 1.12.1

Running simple client connection tests...
Test results: 0.0593 0.0138 0.0120 0.0111 0.0105 (avg 0.0213s)

Running simple tool list tests...
Test results: 0.0039 0.0036 0.0034 0.0050 0.0033 (avg 0.0039s)

Running simple tool call tests...
Test results: 0.0072 0.0058 0.0063 0.0063 0.0062 (avg 0.0064s)

Starting callback server... done
Running in memory OAuth provider construction tests...
Test results: 0.0009 0.0001 0.0000 0.0000 0.0001 (avg 0.0002s)

Running Notion client connection tests (OAuth)...
Test results: 6.3121 11.7071 11.6994 11.6963 11.7797 (avg 10.6389s)

Running Notion list tools tests...
Test results: 10.6288 10.4737 10.3595 10.3114 10.5529 (avg 10.4652s)

Running Notion call tool tests...
Test results: 10.6931 11.1187 13.4962 11.9530 10.8899 (avg 11.6302s)

Stopping callback server... done
Running GitHub client connection tests (PAT)...
Test results: 0.4818 0.2940 0.2908 0.2831 0.2908 (avg 0.3281s)

Running GitHub list tools tests...
Test results: 0.5536 0.1563 0.1076 0.1102 0.1399 (avg 0.2135s)

Running GitHub call tool tests...
Test results: 0.2749 0.2801 0.2645 0.3661 0.3368 (avg 0.3045s)

Finished!
```

## SDK Version 1.13.0 (latest)

```
Starting tests with official Python MCP SDK version 1.13.0

Running simple client connection tests...
Test results: 0.0596 0.0133 0.0116 0.0108 0.0104 (avg 0.0212s)

Running simple tool list tests...
Test results: 0.0040 0.0035 0.0035 0.0053 0.0036 (avg 0.0040s)

Running simple tool call tests...
Test results: 0.0072 0.0060 0.0064 0.0058 0.0064 (avg 0.0064s)

Starting callback server... done
Running in memory OAuth provider construction tests...
Test results: 0.0021 0.0001 0.0000 0.0000 0.0000 (avg 0.0005s)

Running Notion client connection tests (OAuth)...
Test results: 5.4729 11.4962 11.8369 11.6574 11.5804 (avg 10.4088s)

Running Notion list tools tests...
Test results: 10.5502 10.4495 10.4619 10.3530 10.4236 (avg 10.4476s)

Running Notion call tool tests...
Test results: 10.5274 10.8830 10.5276 11.6691 10.5476 (avg 10.8309s)

Stopping callback server... done
Running GitHub client connection tests (PAT)...
Test results: 0.4458 0.2909 0.2915 0.2900 0.2837 (avg 0.3204s)

Running GitHub list tools tests...
Test results: 0.5327 0.1121 0.1792 0.1069 0.1083 (avg 0.2079s)

Running GitHub call tool tests...
Test results: 0.2469 0.2270 0.2424 0.3186 0.2323 (avg 0.2534s)

Finished!
```

# Analysis

These results show that in version 1.12.0 of the Python MCP SDK there was a regression in the performance of clients
with some remote streamable HTTP based servers. *Note that version 1.12.1 is shown and not 1.12.0 due to an unrelated
bug.*

In my tests the Notion MCP server (the only one that shows the performance degradation) is also the only one that I am
authenticating with OAuth. Because of this I profiled the `OAuthClientProvider` class and did not find any performance
concerns. It appears that in the degraded tests the ~10 seconds spent per request are largely delays in communication
with the read and write streams. I don't have the expertise to debug this further. 

Another thing to note is that the latest version of MCP inspector (`@modelcontextprotocol/inspector@0.16.3`) does not
exhibit this performance issue, corroborating the theory that this issue is with the streamable HTTP communication in
the MCP Python SDK.
