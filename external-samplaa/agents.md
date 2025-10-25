Directory structure:
└── getting_started/
    ├── __init__.py
    ├── minimal_sample.py
    ├── agents/
    │   ├── README.md
    │   ├── a2a/
    │   │   ├── README.md
    │   │   └── agent_with_a2a.py
    │   ├── anthropic/
    │   │   ├── README.md
    │   │   └── anthropic_with_openai_chat_client.py
    │   ├── azure_ai/
    │   │   ├── README.md
    │   │   ├── azure_ai_basic.py
    │   │   ├── azure_ai_with_azure_ai_search.py
    │   │   ├── azure_ai_with_bing_grounding.py
    │   │   ├── azure_ai_with_code_interpreter.py
    │   │   ├── azure_ai_with_existing_agent.py
    │   │   ├── azure_ai_with_existing_thread.py
    │   │   ├── azure_ai_with_explicit_settings.py
    │   │   ├── azure_ai_with_file_search.py
    │   │   ├── azure_ai_with_function_tools.py
    │   │   ├── azure_ai_with_hosted_mcp.py
    │   │   ├── azure_ai_with_local_mcp.py
    │   │   ├── azure_ai_with_multiple_tools.py
    │   │   ├── azure_ai_with_openapi_tools.py
    │   │   └── azure_ai_with_thread.py
    │   ├── azure_openai/
    │   │   ├── README.md
    │   │   ├── azure_assistants_basic.py
    │   │   ├── azure_assistants_with_code_interpreter.py
    │   │   ├── azure_assistants_with_existing_assistant.py
    │   │   ├── azure_assistants_with_explicit_settings.py
    │   │   ├── azure_assistants_with_function_tools.py
    │   │   ├── azure_assistants_with_thread.py
    │   │   ├── azure_chat_client_basic.py
    │   │   ├── azure_chat_client_with_explicit_settings.py
    │   │   ├── azure_chat_client_with_function_tools.py
    │   │   ├── azure_chat_client_with_thread.py
    │   │   ├── azure_responses_client_basic.py
    │   │   ├── azure_responses_client_code_interpreter_files.py
    │   │   ├── azure_responses_client_image_analysis.py
    │   │   ├── azure_responses_client_with_code_interpreter.py
    │   │   ├── azure_responses_client_with_explicit_settings.py
    │   │   ├── azure_responses_client_with_function_tools.py
    │   │   ├── azure_responses_client_with_local_mcp.py
    │   │   └── azure_responses_client_with_thread.py
    │   ├── copilotstudio/
    │   │   ├── README.md
    │   │   ├── copilotstudio_basic.py
    │   │   └── copilotstudio_with_explicit_settings.py
    │   ├── custom/
    │   │   ├── README.md
    │   │   ├── custom_agent.py
    │   │   └── custom_chat_client.py
    │   ├── ollama/
    │   │   ├── README.md
    │   │   └── ollama_with_openai_chat_client.py
    │   ├── openai/
    │   │   ├── README.md
    │   │   ├── openai_assistants_basic.py
    │   │   ├── openai_assistants_with_code_interpreter.py
    │   │   ├── openai_assistants_with_existing_assistant.py
    │   │   ├── openai_assistants_with_explicit_settings.py
    │   │   ├── openai_assistants_with_file_search.py
    │   │   ├── openai_assistants_with_function_tools.py
    │   │   ├── openai_assistants_with_thread.py
    │   │   ├── openai_chat_client_basic.py
    │   │   ├── openai_chat_client_with_explicit_settings.py
    │   │   ├── openai_chat_client_with_function_tools.py
    │   │   ├── openai_chat_client_with_local_mcp.py
    │   │   ├── openai_chat_client_with_thread.py
    │   │   ├── openai_chat_client_with_web_search.py
    │   │   ├── openai_responses_client_basic.py
    │   │   ├── openai_responses_client_image_analysis.py
    │   │   ├── openai_responses_client_image_generation.py
    │   │   ├── openai_responses_client_reasoning.py
    │   │   ├── openai_responses_client_with_code_interpreter.py
    │   │   ├── openai_responses_client_with_code_interpreter_files.py
    │   │   ├── openai_responses_client_with_explicit_settings.py
    │   │   ├── openai_responses_client_with_file_search.py
    │   │   ├── openai_responses_client_with_function_tools.py
    │   │   ├── openai_responses_client_with_hosted_mcp.py
    │   │   ├── openai_responses_client_with_local_mcp.py
    │   │   ├── openai_responses_client_with_structured_output.py
    │   │   ├── openai_responses_client_with_thread.py
    │   │   └── openai_responses_client_with_web_search.py
    │   └── resources/
    │       ├── countries.json
    │       └── weather.json
    ├── chat_client/
    │   ├── README.md
    │   ├── azure_ai_chat_client.py
    │   ├── azure_assistants_client.py
    │   ├── azure_chat_client.py
    │   ├── azure_responses_client.py
    │   ├── chat_response_cancellation.py
    │   ├── openai_assistants_client.py
    │   ├── openai_chat_client.py
    │   └── openai_responses_client.py
    ├── context_providers/
    │   ├── simple_context_provider.py
    │   ├── mem0/
    │   │   ├── README.md
    │   │   ├── mem0_basic.py
    │   │   ├── mem0_oss.py
    │   │   └── mem0_threads.py
    │   └── redis/
    │       ├── README.md
    │       ├── redis_basics.py
    │       ├── redis_conversation.py
    │       └── redis_threads.py
    ├── devui/
    │   ├── README.md
    │   ├── in_memory_mode.py
    │   ├── fanout_workflow/
    │   │   ├── __init__.py
    │   │   └── workflow.py
    │   ├── foundry_agent/
    │   │   ├── __init__.py
    │   │   ├── agent.py
    │   │   └── .env.example
    │   ├── spam_workflow/
    │   │   ├── __init__.py
    │   │   └── workflow.py
    │   ├── weather_agent_azure/
    │   │   ├── __init__.py
    │   │   ├── agent.py
    │   │   └── .env.example
    │   └── workflow_agents/
    │       ├── __init__.py
    │       ├── workflow.py
    │       └── .env.example
    ├── evaluation/
    │   └── azure_ai_foundry/
    │       ├── README.md
    │       ├── red_team_agent_sample.py
    │       └── .env.example
    ├── mcp/
    │   ├── README.md
    │   ├── agent_as_mcp_server.py
    │   └── mcp_api_key_auth.py
    ├── middleware/
    │   ├── README.md
    │   ├── agent_and_run_level_middleware.py
    │   ├── chat_middleware.py
    │   ├── class_based_middleware.py
    │   ├── decorator_middleware.py
    │   ├── exception_handling_with_middleware.py
    │   ├── function_based_middleware.py
    │   ├── middleware_termination.py
    │   ├── override_result_with_middleware.py
    │   └── shared_state_middleware.py
    ├── multimodal_input/
    │   ├── README.md
    │   ├── azure_chat_multimodal.py
    │   ├── azure_responses_multimodal.py
    │   └── openai_chat_multimodal.py
    ├── observability/
    │   ├── README.md
    │   ├── __init__.py
    │   ├── advanced_manual_setup_console_output.py
    │   ├── advanced_zero_code.py
    │   ├── agent_observability.py
    │   ├── azure_ai_agent_observability.py
    │   ├── azure_ai_chat_client_with_observability.py
    │   ├── setup_observability_with_env_var.py
    │   ├── setup_observability_with_parameters.py
    │   ├── workflow_observability.py
    │   └── .env.example
    ├── purview_agent/
    │   ├── README.md
    │   └── sample_purview_agent.py
    ├── threads/
    │   ├── README.md
    │   ├── custom_chat_message_store_thread.py
    │   ├── redis_chat_message_store_thread.py
    │   └── suspend_resume_thread.py
    ├── tools/
    │   ├── README.md
    │   ├── ai_tool_with_approval.py
    │   ├── ai_tool_with_approval_and_threads.py
    │   ├── failing_tools.py
    │   └── tool_with_injected_func.py
    └── workflows/
        ├── README.md
        ├── _start-here/
        │   ├── step1_executors_and_edges.py
        │   ├── step2_agents_in_a_workflow.py
        │   └── step3_streaming.py
        ├── agents/
        │   ├── azure_ai_agents_streaming.py
        │   ├── azure_chat_agents_function_bridge.py
        │   ├── azure_chat_agents_streaming.py
        │   ├── azure_chat_agents_tool_calls_with_feedback.py
        │   ├── concurrent_workflow_as_agent.py
        │   ├── custom_agent_executors.py
        │   ├── group_chat_workflow_as_agent.py
        │   ├── magentic_workflow_as_agent.py
        │   ├── sequential_workflow_as_agent.py
        │   ├── workflow_as_agent_human_in_the_loop.py
        │   └── workflow_as_agent_reflection_pattern.py
        ├── checkpoint/
        │   ├── checkpoint_with_human_in_the_loop.py
        │   ├── checkpoint_with_resume.py
        │   └── sub_workflow_checkpoint.py
        ├── composition/
        │   ├── sub_workflow_basics.py
        │   ├── sub_workflow_parallel_requests.py
        │   └── sub_workflow_request_interception.py
        ├── control-flow/
        │   ├── edge_condition.py
        │   ├── multi_selection_edge_group.py
        │   ├── sequential_executors.py
        │   ├── sequential_streaming.py
        │   ├── simple_loop.py
        │   └── switch_case_edge_group.py
        ├── human-in-the-loop/
        │   └── guessing_game_with_human_input.py
        ├── observability/
        │   └── tracing_basics.py
        ├── orchestration/
        │   ├── concurrent_agents.py
        │   ├── concurrent_custom_agent_executors.py
        │   ├── concurrent_custom_aggregator.py
        │   ├── group_chat_prompt_based_manager.py
        │   ├── group_chat_simple_selector.py
        │   ├── handoff_simple.py
        │   ├── handoff_specialist_to_specialist.py
        │   ├── magentic.py
        │   ├── magentic_checkpoint.py
        │   ├── magentic_human_plan_update.py
        │   ├── sequential_agents.py
        │   └── sequential_custom_executors.py
        ├── parallelism/
        │   ├── aggregate_results_of_different_types.py
        │   ├── fan_out_fan_in_edges.py
        │   └── map_reduce_and_visualization.py
        ├── resources/
        │   ├── ambiguous_email.txt
        │   ├── email.txt
        │   ├── long_text.txt
        │   └── spam.txt
        ├── state-management/
        │   └── shared_states_with_agents.py
        └── visualization/
            └── concurrent_with_visualization.py


Files Content:

(Files content cropped to 300k characters, download full ingest to see more)
================================================
FILE: python/samples/getting_started/__init__.py
================================================
[Empty file]


================================================
FILE: python/samples/getting_started/minimal_sample.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIChatClient


def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


agent = OpenAIChatClient().create_agent(
    name="WeatherAgent", instructions="You are a helpful weather agent.", tools=get_weather
)
print(asyncio.run(agent.run("What's the weather like in Seattle?")))



================================================
FILE: python/samples/getting_started/agents/README.md
================================================
# Agent Examples

This folder contains examples demonstrating how to create and use agents with different chat clients from the Agent Framework. Each sub-folder focuses on a specific provider and client type, showing various capabilities like function tools, code interpreter, thread management, structured outputs, image processing, web search, Model Context Protocol (MCP) integration, and more.

## Examples by Provider

### Azure AI Foundry Examples

| Folder | Description |
|--------|-------------|
| **[`azure_ai/`](azure_ai/)** | Create agents using Azure AI Foundry Agent Service with various tools including function tools, code interpreter, MCP integration, and thread management |

### Microsoft Copilot Studio Examples

| Folder | Description |
|--------|-------------|
| **[`copilotstudio/`](copilotstudio/)** | Create agents using Microsoft Copilot Studio with streaming and non-streaming responses, authentication handling, and explicit configuration options |

### Azure OpenAI Examples

| Folder | Description |
|--------|-------------|
| **[`azure_openai/`](azure_openai/)** | Create agents using Azure OpenAI APIs with multiple client types (Assistants, Chat, and Responses clients) supporting function tools, code interpreter, thread management, and more |

### OpenAI Examples

| Folder | Description |
|--------|-------------|
| **[`openai/`](openai/)** | Create agents using OpenAI APIs with comprehensive examples including Assistants, Chat, and Responses clients featuring function tools, code interpreter, file search, web search, MCP integration, image analysis/generation, structured outputs, reasoning, and thread management |

### Anthropic Examples

| Folder | Description |
|--------|-------------|
| **[`anthropic/`](anthropic/)** | Create agents using Anthropic models through OpenAI Chat Client configuration, demonstrating tool calling capabilities |

### Custom Implementation Examples

| Folder | Description |
|--------|-------------|
| **[`custom/`](custom/)** | Create custom agents and chat clients by extending the base framework classes, showing complete control over agent behavior and backend integration |



================================================
FILE: python/samples/getting_started/agents/a2a/README.md
================================================
# A2A Agent Examples

This folder contains examples demonstrating how to create and use agents with the A2A (Agent2Agent) protocol from the `agent_framework` package to communicate with remote A2A agents.

For more information about the A2A protocol specification, visit: https://a2a-protocol.org/latest/
## Examples

| File | Description |
|------|-------------|
| [`agent_with_a2a.py`](agent_with_a2a.py) | The simplest way to connect to and use a single A2A agent. Demonstrates agent discovery via agent cards and basic message exchange using the A2A protocol. |

## Environment Variables

Make sure to set the following environment variables before running the example:

### Required
- `A2A_AGENT_HOST`: URL of a single A2A agent (for simple sample, e.g., `http://localhost:5001/`)


## Quick Testing with .NET A2A Servers

For quick testing and demonstration, you can use the pre-built .NET A2A servers from this repository:

**Quick Testing Reference**: Use the .NET A2A Client Server sample at:
`..\agent-framework\dotnet\samples\A2AClientServer`

### Run Python A2A Sample
```powershell
# Simple A2A sample (single agent)
uv run python agent_with_a2a.py
```



================================================
FILE: python/samples/getting_started/agents/a2a/agent_with_a2a.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

import httpx
from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent

"""
Agent2Agent (A2A) Protocol Integration Sample

This sample demonstrates how to connect to and communicate with external agents using
the A2A protocol. A2A is a standardized communication protocol that enables interoperability
between different agent systems, allowing agents built with different frameworks and
technologies to communicate seamlessly.

For more information about the A2A protocol specification, visit: https://a2a-protocol.org/latest/

Key concepts demonstrated:
- Discovering A2A-compliant agents using AgentCard resolution
- Creating A2AAgent instances to wrap external A2A endpoints
- Converting Agent Framework messages to A2A protocol format
- Handling A2A responses (Messages and Tasks) back to framework types

To run this sample:
1. Set the A2A_AGENT_HOST environment variable to point to an A2A-compliant agent endpoint
   Example: export A2A_AGENT_HOST="https://your-a2a-agent.example.com"
2. Ensure the target agent exposes its AgentCard at /.well-known/agent.json
3. Run: uv run python agent_with_a2a.py

The sample will:
- Connect to the specified A2A agent endpoint
- Retrieve and parse the agent's capabilities via its AgentCard
- Send a message using the A2A protocol
- Display the agent's response

Visit the README.md for more details on setting up and running A2A agents.
"""


async def main():
    """Demonstrates connecting to and communicating with an A2A-compliant agent."""
    # Get A2A agent host from environment
    a2a_agent_host = os.getenv("A2A_AGENT_HOST")
    if not a2a_agent_host:
        raise ValueError("A2A_AGENT_HOST environment variable is not set")

    print(f"Connecting to A2A agent at: {a2a_agent_host}")

    # Initialize A2ACardResolver
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        resolver = A2ACardResolver(httpx_client=http_client, base_url=a2a_agent_host)

        # Get agent card
        agent_card = await resolver.get_agent_card(relative_card_path="/.well-known/agent.json")
        print(f"Found agent: {agent_card.name} - {agent_card.description}")

        # Create A2A agent instance
        agent = A2AAgent(
            name=agent_card.name,
            description=agent_card.description,
            agent_card=agent_card,
            url=a2a_agent_host,
        )

        # Invoke the agent and output the result
        print("\nSending message to A2A agent...")
        response = await agent.run("Tell me a joke about a pirate.")

        # Print the response
        print("\nAgent Response:")
        for message in response.messages:
            print(message.text)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/anthropic/README.md
================================================
# Anthropic Examples

This folder contains examples demonstrating how to use Anthropic's Claude models with the Agent Framework.

## Examples

| File | Description |
|------|-------------|
| [`anthropic_with_openai_chat_client.py`](anthropic_with_openai_chat_client.py) | Demonstrates how to configure OpenAI Chat Client to use Anthropic's Claude models. Shows both streaming and non-streaming responses with tool calling capabilities. |

## Environment Variables

Set the following environment variables before running the examples:

- `ANTHROPIC_API_KEY`: Your Anthropic API key (get one from [Anthropic Console](https://console.anthropic.com/))
- `ANTHROPIC_MODEL`: The Claude model to use (e.g., `claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307`)




================================================
FILE: python/samples/getting_started/agents/anthropic/anthropic_with_openai_chat_client.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIChatClient

"""
Anthropic with OpenAI Chat Client Example

This sample demonstrates using Anthropic models through OpenAI Chat Client by
configuring the base URL to point to Anthropic's API for cross-provider compatibility.
"""


def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    agent = OpenAIChatClient(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        base_url="https://api.anthropic.com/v1/",
        model_id=os.getenv("ANTHROPIC_MODEL"),
    ).create_agent(
        name="WeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Seattle?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Result: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    agent = OpenAIChatClient(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        base_url="https://api.anthropic.com/v1/",
        model_id=os.getenv("ANTHROPIC_MODEL"),
    ).create_agent(
        name="WeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Portland?"
    print(f"User: {query}")
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run_stream(query):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


async def main() -> None:
    print("=== Anthropic with OpenAI Chat Client Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/README.md
================================================
# Azure AI Agent Examples

This folder contains examples demonstrating different ways to create and use agents with the Azure AI chat client from the `agent_framework.azure` package.

## Examples

| File | Description |
|------|-------------|
| [`azure_ai_basic.py`](azure_ai_basic.py) | The simplest way to create an agent using `ChatAgent` with `AzureAIAgentClient`. It automatically handles all configuration using environment variables. |
| [`azure_ai_with_bing_grounding.py`](azure_ai_with_bing_grounding.py) | Shows how to use Bing Grounding search with Azure AI agents to find real-time information from the web. Demonstrates web search capabilities with proper source citations and comprehensive error handling. |
| [`azure_ai_with_code_interpreter.py`](azure_ai_with_code_interpreter.py) | Shows how to use the HostedCodeInterpreterTool with Azure AI agents to write and execute Python code. Includes helper methods for accessing code interpreter data from response chunks. |
| [`azure_ai_with_existing_agent.py`](azure_ai_with_existing_agent.py) | Shows how to work with a pre-existing agent by providing the agent ID to the Azure AI chat client. This example also demonstrates proper cleanup of manually created agents. |
| [`azure_ai_with_existing_thread.py`](azure_ai_with_existing_thread.py) | Shows how to work with a pre-existing thread by providing the thread ID to the Azure AI chat client. This example also demonstrates proper cleanup of manually created threads. |
| [`azure_ai_with_explicit_settings.py`](azure_ai_with_explicit_settings.py) | Shows how to create an agent with explicitly configured `AzureAIAgentClient` settings, including project endpoint, model deployment, credentials, and agent name. |
| [`azure_ai_with_azure_ai_search.py`](azure_ai_with_azure_ai_search.py) | Demonstrates how to use Azure AI Search with Azure AI agents to search through indexed data. Shows how to configure search parameters, query types, and integrate with existing search indexes. |
| [`azure_ai_with_file_search.py`](azure_ai_with_file_search.py) | Demonstrates how to use the HostedFileSearchTool with Azure AI agents to search through uploaded documents. Shows file upload, vector store creation, and querying document content. Includes both streaming and non-streaming examples. |
| [`azure_ai_with_function_tools.py`](azure_ai_with_function_tools.py) | Demonstrates how to use function tools with agents. Shows both agent-level tools (defined when creating the agent) and query-level tools (provided with specific queries). |
| [`azure_ai_with_hosted_mcp.py`](azure_ai_with_hosted_mcp.py) | Shows how to integrate Azure AI agents with hosted Model Context Protocol (MCP) servers for enhanced functionality and tool integration. Demonstrates remote MCP server connections and tool discovery. |
| [`azure_ai_with_local_mcp.py`](azure_ai_with_local_mcp.py) | Shows how to integrate Azure AI agents with local Model Context Protocol (MCP) servers for enhanced functionality and tool integration. Demonstrates both agent-level and run-level tool configuration. |
| [`azure_ai_with_multiple_tools.py`](azure_ai_with_multiple_tools.py) | Demonstrates how to use multiple tools together with Azure AI agents, including web search, MCP servers, and function tools. Shows coordinated multi-tool interactions and approval workflows. |
| [`azure_ai_with_openapi_tools.py`](azure_ai_with_openapi_tools.py) | Demonstrates how to use OpenAPI tools with Azure AI agents to integrate external REST APIs. Shows OpenAPI specification loading, anonymous authentication, thread context management, and coordinated multi-API conversations using weather and countries APIs. |
| [`azure_ai_with_thread.py`](azure_ai_with_thread.py) | Demonstrates thread management with Azure AI agents, including automatic thread creation for stateless conversations and explicit thread management for maintaining conversation context across multiple interactions. |

## Environment Variables

Before running the examples, you need to set up your environment variables. You can do this in one of two ways:

### Option 1: Using a .env file (Recommended)

1. Copy the `.env.example` file from the `python` directory to create a `.env` file:
   ```bash
   cp ../../.env.example ../../.env
   ```

2. Edit the `.env` file and add your values:
   ```
   AZURE_AI_PROJECT_ENDPOINT="your-project-endpoint"
   AZURE_AI_MODEL_DEPLOYMENT_NAME="your-model-deployment-name"
   ```

3. For samples using Bing Grounding search (like `azure_ai_with_bing_grounding.py` and `azure_ai_with_multiple_tools.py`), you'll also need either:
   ```
   BING_CONNECTION_NAME="bing-grounding-connection"
   # OR
   BING_CONNECTION_ID="your-bing-connection-id"
   ```

   To get your Bing connection details:
   - Go to [Azure AI Foundry portal](https://ai.azure.com)
   - Navigate to your project's "Connected resources" section
   - Add a new connection for "Grounding with Bing Search"
   - Copy either the connection name or ID

### Option 2: Using environment variables directly

Set the environment variables in your shell:

```bash
export AZURE_AI_PROJECT_ENDPOINT="your-project-endpoint"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="your-model-deployment-name"
export BING_CONNECTION_NAME="your-bing-connection-name"  # Optional, only needed for web search samples
# OR
export BING_CONNECTION_ID="your-bing-connection-id"  # Alternative to BING_CONNECTION_NAME
```

### Required Variables

- `AZURE_AI_PROJECT_ENDPOINT`: Your Azure AI project endpoint (required for all examples)
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`: The name of your model deployment (required for all examples)

### Optional Variables

- `BING_CONNECTION_NAME` or `BING_CONNECTION_ID`: Your Bing connection name or ID (required for `azure_ai_with_bing_grounding.py` and `azure_ai_with_multiple_tools.py`)



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_basic.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Agent Basic Example

This sample demonstrates basic usage of AzureAIAgentClient to create agents with automatic
lifecycle management. Shows both streaming and non-streaming responses with function tools.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    # Since no Agent ID is provided, the agent will be automatically created
    # and deleted after getting a response
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="WeatherAgent",
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent,
    ):
        query = "What's the weather like in Seattle?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    # Since no Agent ID is provided, the agent will be automatically created
    # and deleted after getting a response
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="WeatherAgent",
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent,
    ):
        query = "What's the weather like in Portland?"
        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream(query):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")


async def main() -> None:
    print("=== Basic Azure AI Chat Client Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_azure_ai_search.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import ChatAgent, HostedFileSearchTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

"""
Azure AI Agent with Azure AI Search Example

This sample demonstrates how to create an Azure AI agent that uses Azure AI Search
to search through indexed hotel data and answer user questions about hotels.

Prerequisites:
1. Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables
2. Ensure you have an Azure AI Search connection configured in your Azure AI project
3. The search index "hotels-sample-index" should exist in your Azure AI Search service
   (you can create this using the Azure portal with sample hotel data)

Environment variables:
- AZURE_AI_PROJECT_ENDPOINT: Your Azure AI project endpoint
- AZURE_AI_MODEL_DEPLOYMENT_NAME: The name of your model deployment
"""

# Test queries to verify Azure AI Search is working with the hotels-sample-index
USER_INPUTS = [
    "Search the hotel database for Stay-Kay City Hotel and give me detailed information.",
]


async def main() -> None:
    """Main function demonstrating Azure AI agent with Azure AI Search capabilities."""

    # 1. Create Azure AI Search tool using HostedFileSearchTool
    # The tool will automatically use the default Azure AI Search connection from your project
    azure_ai_search_tool = HostedFileSearchTool(
        additional_properties={
            "index_name": "hotels-sample-index",  # Name of your search index
            "query_type": "simple",  # Use simple search
            "top_k": 10,  # Get more comprehensive results
        },
    )

    # 2. Use AzureAIAgentClient as async context manager for automatic cleanup
    async with (
        AzureAIAgentClient(async_credential=AzureCliCredential()) as client,
        ChatAgent(
            chat_client=client,
            name="HotelSearchAgent",
            instructions=("You are a helpful travel assistant that searches hotel information."),
            tools=azure_ai_search_tool,
        ) as agent,
    ):
        print("=== Azure AI Agent with Azure AI Search ===")
        print("This agent can search through hotel data to help you find accommodations.\n")

        # 3. Simulate conversation with the agent
        for user_input in USER_INPUTS:
            print(f"User: {user_input}")
            print("Agent: ", end="", flush=True)

            # Stream the response for better user experience
            async for chunk in agent.run_stream(user_input):
                if chunk.text:
                    print(chunk.text, end="", flush=True)
            print("\n" + "=" * 50 + "\n")

        print("Hotel search conversation completed!")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_bing_grounding.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import ChatAgent, HostedWebSearchTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

"""
The following sample demonstrates how to create an Azure AI agent that
uses Bing Grounding search to find real-time information from the web.

Prerequisites:
1. A connected Grounding with Bing Search resource in your Azure AI project
2. Set either BING_CONNECTION_NAME or BING_CONNECTION_ID environment variable
   Example: BING_CONNECTION_NAME="bing-grounding-connection"
   Example: BING_CONNECTION_ID="your-bing-connection-id"

To set up Bing Grounding:
1. Go to Azure AI Foundry portal (https://ai.azure.com)
2. Navigate to your project's "Connected resources" section
3. Add a new connection for "Grounding with Bing Search"
4. Copy either the connection name or ID and set the appropriate environment variable
"""


async def main() -> None:
    """Main function demonstrating Azure AI agent with Bing Grounding search."""
    # 1. Create Bing Grounding search tool using HostedWebSearchTool
    # The connection_name or ID will be automatically picked up from environment variable
    bing_search_tool = HostedWebSearchTool(
        name="Bing Grounding Search",
        description="Search the web for current information using Bing",
    )

    # 2. Use AzureAIAgentClient as async context manager for automatic cleanup
    async with (
        AzureAIAgentClient(async_credential=AzureCliCredential()) as client,
        ChatAgent(
            chat_client=client,
            name="BingSearchAgent",
            instructions=(
                "You are a helpful assistant that can search the web for current information. "
                "Use the Bing search tool to find up-to-date information and provide accurate, "
                "well-sourced answers. Always cite your sources when possible."
            ),
            tools=bing_search_tool,
        ) as agent,
    ):
        # 4. Demonstrate agent capabilities with web search
        print("=== Azure AI Agent with Bing Grounding Search ===\n")

        user_input = "What is the most popular programming language?"
        print(f"User: {user_input}")
        response = await agent.run(user_input)
        print(f"Agent: {response.text}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_code_interpreter.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import AgentRunResponse, ChatResponseUpdate, HostedCodeInterpreterTool
from agent_framework.azure import AzureAIAgentClient
from azure.ai.agents.models import (
    RunStepDeltaCodeInterpreterDetailItemObject,
)
from azure.identity.aio import AzureCliCredential

"""
Azure AI Agent with Code Interpreter Example

This sample demonstrates using HostedCodeInterpreterTool with Azure AI Agents
for Python code execution and mathematical problem solving.
"""


def print_code_interpreter_inputs(response: AgentRunResponse) -> None:
    """Helper method to access code interpreter data."""

    print("\nCode Interpreter Inputs during the run:")
    if response.raw_representation is None:
        return
    for chunk in response.raw_representation:
        if isinstance(chunk, ChatResponseUpdate) and isinstance(
            chunk.raw_representation, RunStepDeltaCodeInterpreterDetailItemObject
        ):
            print(chunk.raw_representation.input, end="")
    print("\n")


async def main() -> None:
    """Example showing how to use the HostedCodeInterpreterTool with Azure AI."""
    print("=== Azure AI Agent with Code Interpreter Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential) as chat_client,
    ):
        agent = chat_client.create_agent(
            name="CodingAgent",
            instructions=("You are a helpful assistant that can write and execute Python code to solve problems."),
            tools=HostedCodeInterpreterTool(),
        )
        query = "Generate the factorial of 100 using python code, show the code and execute it."
        print(f"User: {query}")
        response = await AgentRunResponse.from_agent_response_generator(agent.run_stream(query))
        print(f"Agent: {response}")
        # To review the code interpreter outputs, you can access
        # them from the response raw_representations, just uncomment the next line:
        # print_code_interpreter_inputs(response)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_existing_agent.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential

"""
Azure AI Agent with Existing Agent Example

This sample demonstrates working with pre-existing Azure AI Agents by providing
agent IDs, showing agent reuse patterns for production scenarios.
"""


async def main() -> None:
    print("=== Azure AI Chat Client with Existing Agent ===")

    # Create the client
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as client,
    ):
        azure_ai_agent = await client.agents.create_agent(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            # Create remote agent with default instructions
            # These instructions will persist on created agent for every run.
            instructions="End each response with [END].",
        )

        chat_client = AzureAIAgentClient(project_client=client, agent_id=azure_ai_agent.id)

        try:
            async with ChatAgent(
                chat_client=chat_client,
                # Instructions here are applicable only to this ChatAgent instance
                # These instructions will be combined with instructions on existing remote agent.
                # The final instructions during the execution will look like:
                # "'End each response with [END]. Respond with 'Hello World' only'"
                instructions="Respond with 'Hello World' only",
            ) as agent:
                query = "How are you?"
                print(f"User: {query}")
                result = await agent.run(query)
                # Based on local and remote instructions, the result will be
                # 'Hello World [END]'.
                print(f"Agent: {result}\n")
        finally:
            # Clean up the agent manually
            await client.agents.delete_agent(azure_ai_agent.id)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_existing_thread.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Agent with Existing Thread Example

This sample demonstrates working with pre-existing conversation threads
by providing thread IDs for thread reuse patterns.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    print("=== Azure AI Chat Client with Existing Thread ===")

    # Create the client
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as client,
    ):
        # Create an thread that will persist
        created_thread = await client.agents.threads.create()

        try:
            async with ChatAgent(
                # passing in the client is optional here, so if you take the agent_id from the portal
                # you can use it directly without the two lines above.
                chat_client=AzureAIAgentClient(project_client=client),
                instructions="You are a helpful weather agent.",
                tools=get_weather,
            ) as agent:
                thread = agent.get_new_thread(service_thread_id=created_thread.id)
                assert thread.is_initialized
                result = await agent.run("What's the weather like in Tokyo?", thread=thread)
                print(f"Result: {result}\n")
        finally:
            # Clean up the thread manually
            await client.agents.threads.delete(created_thread.id)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_explicit_settings.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Agent with Explicit Settings Example

This sample demonstrates creating Azure AI Agents with explicit configuration
settings rather than relying on environment variable defaults.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    print("=== Azure AI Chat Client with Explicit Settings ===")

    # Since no Agent ID is provided, the agent will be automatically created
    # and deleted after getting a response
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(
                project_endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
                model_deployment_name=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                async_credential=credential,
                agent_name="WeatherAgent",
            ),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent,
    ):
        result = await agent.run("What's the weather like in New York?")
        print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_file_search.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from pathlib import Path

from agent_framework import ChatAgent, HostedFileSearchTool, HostedVectorStoreContent
from agent_framework_azure_ai import AzureAIAgentClient
from azure.ai.agents.models import FileInfo, VectorStore
from azure.identity.aio import AzureCliCredential

"""
The following sample demonstrates how to create a simple, Azure AI agent that
uses a file search tool to answer user questions.
"""


# Simulate a conversation with the agent
USER_INPUTS = [
    "Who is the youngest employee?",
    "Who works in sales?",
    "I have a customer request, who can help me?",
]


async def main() -> None:
    """Main function demonstrating Azure AI agent with file search capabilities."""
    client = AzureAIAgentClient(async_credential=AzureCliCredential())
    file: FileInfo | None = None
    vector_store: VectorStore | None = None

    try:
        # 1. Upload file and create vector store
        pdf_file_path = Path(__file__).parent.parent / "resources" / "employees.pdf"
        print(f"Uploading file from: {pdf_file_path}")

        file = await client.project_client.agents.files.upload_and_poll(
            file_path=str(pdf_file_path), purpose="assistants"
        )
        print(f"Uploaded file, file ID: {file.id}")

        vector_store = await client.project_client.agents.vector_stores.create_and_poll(
            file_ids=[file.id], name="my_vectorstore"
        )
        print(f"Created vector store, vector store ID: {vector_store.id}")

        # 2. Create file search tool with uploaded resources
        file_search_tool = HostedFileSearchTool(inputs=[HostedVectorStoreContent(vector_store_id=vector_store.id)])

        # 3. Create an agent with file search capabilities
        # The tool_resources are automatically extracted from HostedFileSearchTool
        async with ChatAgent(
            chat_client=client,
            name="EmployeeSearchAgent",
            instructions=(
                "You are a helpful assistant that can search through uploaded employee files "
                "to answer questions about employees."
            ),
            tools=file_search_tool,
        ) as agent:
            # 4. Simulate conversation with the agent
            for user_input in USER_INPUTS:
                print(f"# User: '{user_input}'")
                response = await agent.run(user_input)
                print(f"# Agent: {response.text}")

            # 5. Cleanup: Delete the vector store and file
            try:
                if vector_store:
                    await client.project_client.agents.vector_stores.delete(vector_store.id)
                if file:
                    await client.project_client.agents.files.delete(file.id)
            except Exception:
                # Ignore cleanup errors to avoid masking issues
                pass
    finally:
        # 6. Cleanup: Delete the vector store and file in case of eariler failure to prevent orphaned resources.

        # Refreshing the client is required since chat agent closes it
        client = AzureAIAgentClient(async_credential=AzureCliCredential())
        try:
            if vector_store:
                await client.project_client.agents.vector_stores.delete(vector_store.id)
            if file:
                await client.project_client.agents.files.delete(file.id)
        except Exception:
            # Ignore cleanup errors to avoid masking issues
            pass
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_function_tools.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from datetime import datetime, timezone
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Agent with Function Tools Example

This sample demonstrates function tool integration with Azure AI Agents,
showing both agent-level and query-level tool configuration patterns.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions="You are a helpful assistant that can provide weather and time information.",
            tools=[get_weather, get_time],  # Tools defined at agent creation
        ) as agent,
    ):
        # First query - agent can use weather tool
        query1 = "What's the weather like in New York?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"Agent: {result1}\n")

        # Second query - agent can use time tool
        query2 = "What's the current UTC time?"
        print(f"User: {query2}")
        result2 = await agent.run(query2)
        print(f"Agent: {result2}\n")

        # Third query - agent can use both tools if needed
        query3 = "What's the weather in London and what's the current UTC time?"
        print(f"User: {query3}")
        result3 = await agent.run(query3)
        print(f"Agent: {result3}\n")


async def tools_on_run_level() -> None:
    """Example showing tools passed to the run method."""
    print("=== Tools Passed to Run Method ===")

    # Agent created without tools
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions="You are a helpful assistant.",
            # No tools defined here
        ) as agent,
    ):
        # First query with weather tool
        query1 = "What's the weather like in Seattle?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, tools=[get_weather])  # Tool passed to run method
        print(f"Agent: {result1}\n")

        # Second query with time tool
        query2 = "What's the current UTC time?"
        print(f"User: {query2}")
        result2 = await agent.run(query2, tools=[get_time])  # Different tool for this query
        print(f"Agent: {result2}\n")

        # Third query with multiple tools
        query3 = "What's the weather in Chicago and what's the current UTC time?"
        print(f"User: {query3}")
        result3 = await agent.run(query3, tools=[get_weather, get_time])  # Multiple tools
        print(f"Agent: {result3}\n")


async def mixed_tools_example() -> None:
    """Example showing both agent-level tools and run-method tools."""
    print("=== Mixed Tools Example (Agent + Run Method) ===")

    # Agent created with some base tools
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions="You are a comprehensive assistant that can help with various information requests.",
            tools=[get_weather],  # Base tool available for all queries
        ) as agent,
    ):
        # Query using both agent tool and additional run-method tools
        query = "What's the weather in Denver and what's the current UTC time?"
        print(f"User: {query}")

        # Agent has access to get_weather (from creation) + additional tools from run method
        result = await agent.run(
            query,
            tools=[get_time],  # Additional tools for this specific query
        )
        print(f"Agent: {result}\n")


async def main() -> None:
    print("=== Azure AI Chat Client Agent with Function Tools Examples ===\n")

    await tools_on_agent_level()
    await tools_on_run_level()
    await mixed_tools_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_hosted_mcp.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Any

from agent_framework import AgentProtocol, AgentThread, HostedMCPTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

"""
Azure AI Agent with Hosted MCP Example

This sample demonstrates integration of Azure AI Agents with hosted Model Context Protocol (MCP)
servers, including user approval workflows for function call security.
"""


async def handle_approvals_with_thread(query: str, agent: "AgentProtocol", thread: "AgentThread"):
    """Here we let the thread deal with the previous responses, and we just rerun with the approval."""
    from agent_framework import ChatMessage

    result = await agent.run(query, thread=thread, store=True)
    while len(result.user_input_requests) > 0:
        new_input: list[Any] = []
        for user_input_needed in result.user_input_requests:
            print(
                f"User Input Request for function from {agent.name}: {user_input_needed.function_call.name}"
                f" with arguments: {user_input_needed.function_call.arguments}"
            )
            user_approval = input("Approve function call? (y/n): ")
            new_input.append(
                ChatMessage(
                    role="user",
                    contents=[user_input_needed.create_response(user_approval.lower() == "y")],
                )
            )
        result = await agent.run(new_input, thread=thread, store=True)
    return result


async def main() -> None:
    """Example showing Hosted MCP tools for a Azure AI Agent."""
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential) as chat_client,
    ):
        # enable azure-ai observability
        await chat_client.setup_azure_ai_observability()
        agent = chat_client.create_agent(
            name="DocsAgent",
            instructions="You are a helpful assistant that can help with microsoft documentation questions.",
            tools=HostedMCPTool(
                name="Microsoft Learn MCP",
                url="https://learn.microsoft.com/api/mcp",
            ),
        )
        thread = agent.get_new_thread()
        # First query
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        result1 = await handle_approvals_with_thread(query1, agent, thread)
        print(f"{agent.name}: {result1}\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        result2 = await handle_approvals_with_thread(query2, agent, thread)
        print(f"{agent.name}: {result2}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_local_mcp.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

"""
Azure AI Agent with Local MCP Example

This sample demonstrates integration of Azure AI Agents with local Model Context Protocol (MCP)
servers, showing both agent-level and run-level tool configuration patterns.
"""


async def mcp_tools_on_run_level() -> None:
    """Example showing MCP tools defined when running the agent."""
    print("=== Tools Defined on Run Level ===")

    # Tools are provided when running the agent
    # This means we have to ensure we connect to the MCP server before running the agent
    # and pass the tools to the run method.
    async with (
        AzureCliCredential() as credential,
        MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
        ) as mcp_server,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            name="DocsAgent",
            instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        ) as agent,
    ):
        # First query
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, tools=mcp_server)
        print(f"{agent.name}: {result1}\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        result2 = await agent.run(query2, tools=mcp_server)
        print(f"{agent.name}: {result2}\n")


async def mcp_tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    # The agent will connect to the MCP server through its context manager.
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="DocsAgent",
            instructions="You are a helpful assistant that can help with microsoft documentation questions.",
            tools=MCPStreamableHTTPTool(  # Tools defined at agent creation
                name="Microsoft Learn MCP",
                url="https://learn.microsoft.com/api/mcp",
            ),
        ) as agent,
    ):
        # First query
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"{agent.name}: {result1}\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        result2 = await agent.run(query2)
        print(f"{agent.name}: {result2}\n")


async def main() -> None:
    print("=== Azure AI Chat Client Agent with MCP Tools Examples ===\n")

    await mcp_tools_on_agent_level()
    await mcp_tools_on_run_level()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_multiple_tools.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from datetime import datetime, timezone
from typing import Any

from agent_framework import (
    AgentProtocol,
    AgentThread,
    HostedMCPTool,
    HostedWebSearchTool,
)
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

"""
Azure AI Agent with Multiple Tools Example

This sample demonstrates integrating multiple tools (MCP and Web Search) with Azure AI Agents,
including user approval workflows for function call security.

Prerequisites:
1. Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME environment variables
2. For Bing search functionality, set BING_CONNECTION_ID environment variable to your Bing connection ID
   Example: BING_CONNECTION_ID="/subscriptions/{subscription-id}/resourceGroups/{resource-group}/
            providers/Microsoft.CognitiveServices/accounts/{ai-service-name}/projects/{project-name}/
            connections/{connection-name}"

To set up Bing Grounding:
1. Go to Azure AI Foundry portal (https://ai.azure.com)
2. Navigate to your project's "Connected resources" section
3. Add a new connection for "Grounding with Bing Search"
4. Copy the connection ID and set it as the BING_CONNECTION_ID environment variable
"""


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def handle_approvals_with_thread(query: str, agent: "AgentProtocol", thread: "AgentThread"):
    """Here we let the thread deal with the previous responses, and we just rerun with the approval."""
    from agent_framework import ChatMessage

    result = await agent.run(query, thread=thread, store=True)
    while len(result.user_input_requests) > 0:
        new_input: list[Any] = []
        for user_input_needed in result.user_input_requests:
            print(
                f"User Input Request for function from {agent.name}: {user_input_needed.function_call.name}"
                f" with arguments: {user_input_needed.function_call.arguments}"
            )
            user_approval = input("Approve function call? (y/n): ")
            new_input.append(
                ChatMessage(
                    role="user",
                    contents=[user_input_needed.create_response(user_approval.lower() == "y")],
                )
            )
        result = await agent.run(new_input, thread=thread, store=True)
    return result


async def main() -> None:
    """Example showing Hosted MCP tools for a Azure AI Agent."""
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential) as chat_client,
    ):
        # enable azure-ai observability
        await chat_client.setup_azure_ai_observability()
        agent = chat_client.create_agent(
            name="DocsAgent",
            instructions="You are a helpful assistant that can help with microsoft documentation questions.",
            tools=[
                HostedMCPTool(
                    name="Microsoft Learn MCP",
                    url="https://learn.microsoft.com/api/mcp",
                ),
                HostedWebSearchTool(count=5),
                get_time,
            ],
        )
        thread = agent.get_new_thread()
        # First query
        query1 = "How to create an Azure storage account using az cli and what time is it?"
        print(f"User: {query1}")
        result1 = await handle_approvals_with_thread(query1, agent, thread)
        print(f"{agent.name}: {result1}\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework and use a web search to see what is Reddit saying about it?"
        print(f"User: {query2}")
        result2 = await handle_approvals_with_thread(query2, agent, thread)
        print(f"{agent.name}: {result2}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_openapi_tools.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
from pathlib import Path
from typing import Any

from agent_framework import ChatAgent
from agent_framework_azure_ai import AzureAIAgentClient
from azure.ai.agents.models import OpenApiAnonymousAuthDetails, OpenApiTool
from azure.identity.aio import AzureCliCredential

"""
The following sample demonstrates how to create a simple, Azure AI agent that
uses OpenAPI tools to answer user questions.
"""

# Simulate a conversation with the agent
USER_INPUTS = [
    "What is the name and population of the country that uses currency with abbreviation THB?",
    "What is the current weather in the capital city of that country?",
]


def load_openapi_specs() -> tuple[dict[str, Any], dict[str, Any]]:
    """Load OpenAPI specification files."""
    resources_path = Path(__file__).parent.parent / "resources"

    with open(resources_path / "weather.json") as weather_file:
        weather_spec = json.load(weather_file)

    with open(resources_path / "countries.json") as countries_file:
        countries_spec = json.load(countries_file)

    return weather_spec, countries_spec


async def main() -> None:
    """Main function demonstrating Azure AI agent with OpenAPI tools."""
    # 1. Load OpenAPI specifications (synchronous operation)
    weather_openapi_spec, countries_openapi_spec = load_openapi_specs()

    # 2. Use AzureAIAgentClient as async context manager for automatic cleanup
    async with AzureAIAgentClient(async_credential=AzureCliCredential()) as client:
        # 3. Create OpenAPI tools using Azure AI's OpenApiTool
        auth = OpenApiAnonymousAuthDetails()

        openapi_weather = OpenApiTool(
            name="get_weather",
            spec=weather_openapi_spec,
            description="Retrieve weather information for a location using wttr.in service",
            auth=auth,
        )

        openapi_countries = OpenApiTool(
            name="get_country_info",
            spec=countries_openapi_spec,
            description="Retrieve country information including population and capital city",
            auth=auth,
        )

        # 4. Create an agent with OpenAPI tools
        # Note: We need to pass the Azure AI native OpenApiTool definitions directly
        # since the agent framework doesn't have a HostedOpenApiTool wrapper yet
        async with ChatAgent(
            chat_client=client,
            name="OpenAPIAgent",
            instructions=(
                "You are a helpful assistant that can search for country information "
                "and weather data using APIs. When asked about countries, use the country "
                "API to find information. When asked about weather, use the weather API. "
                "Provide clear, informative answers based on the API results."
            ),
            # Pass the raw tool definitions from Azure AI's OpenApiTool
            tools=[*openapi_countries.definitions, *openapi_weather.definitions],
        ) as agent:
            # 5. Simulate conversation with the agent maintaining thread context
            print("=== Azure AI Agent with OpenAPI Tools ===\n")

            # Create a thread to maintain conversation context across multiple runs
            thread = agent.get_new_thread()

            for user_input in USER_INPUTS:
                print(f"User: {user_input}")
                # Pass the thread to maintain context across multiple agent.run() calls
                response = await agent.run(user_input, thread=thread)
                print(f"Agent: {response.text}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_ai/azure_ai_with_thread.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework import AgentThread, ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Agent with Thread Management Example

This sample demonstrates thread management with Azure AI Agents, comparing
automatic thread creation with explicit thread management for persistent context.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def example_with_automatic_thread_creation() -> None:
    """Example showing automatic thread creation (service-managed thread)."""
    print("=== Automatic Thread Creation Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent,
    ):
        # First conversation - no thread provided, will be created automatically
        first_query = "What's the weather like in Seattle?"
        print(f"User: {first_query}")
        first_result = await agent.run(first_query)
        print(f"Agent: {first_result.text}")

        # Second conversation - still no thread provided, will create another new thread
        second_query = "What was the last city I asked about?"
        print(f"\nUser: {second_query}")
        second_result = await agent.run(second_query)
        print(f"Agent: {second_result.text}")
        print("Note: Each call creates a separate thread, so the agent doesn't remember previous context.\n")


async def example_with_thread_persistence() -> None:
    """Example showing thread persistence across multiple conversations."""
    print("=== Thread Persistence Example ===")
    print("Using the same thread across multiple conversations to maintain context.\n")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent,
    ):
        # Create a new thread that will be reused
        thread = agent.get_new_thread()

        # First conversation
        first_query = "What's the weather like in Tokyo?"
        print(f"User: {first_query}")
        first_result = await agent.run(first_query, thread=thread)
        print(f"Agent: {first_result.text}")

        # Second conversation using the same thread - maintains context
        second_query = "How about London?"
        print(f"\nUser: {second_query}")
        second_result = await agent.run(second_query, thread=thread)
        print(f"Agent: {second_result.text}")

        # Third conversation - agent should remember both previous cities
        third_query = "Which of the cities I asked about has better weather?"
        print(f"\nUser: {third_query}")
        third_result = await agent.run(third_query, thread=thread)
        print(f"Agent: {third_result.text}")
        print("Note: The agent remembers context from previous messages in the same thread.\n")


async def example_with_existing_thread_id() -> None:
    """Example showing how to work with an existing thread ID from the service."""
    print("=== Existing Thread ID Example ===")
    print("Using a specific thread ID to continue an existing conversation.\n")

    # First, create a conversation and capture the thread ID
    existing_thread_id = None

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with (
        AzureCliCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(async_credential=credential),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent,
    ):
        # Start a conversation and get the thread ID
        thread = agent.get_new_thread()
        first_query = "What's the weather in Paris?"
        print(f"User: {first_query}")
        first_result = await agent.run(first_query, thread=thread)
        print(f"Agent: {first_result.text}")

        # The thread ID is set after the first response
        existing_thread_id = thread.service_thread_id
        print(f"Thread ID: {existing_thread_id}")

    if existing_thread_id:
        print("\n--- Continuing with the same thread ID in a new agent instance ---")

        # Create a new agent instance but use the existing thread ID
        async with (
            AzureCliCredential() as credential,
            ChatAgent(
                chat_client=AzureAIAgentClient(thread_id=existing_thread_id, async_credential=credential),
                instructions="You are a helpful weather agent.",
                tools=get_weather,
            ) as agent,
        ):
            # Create a thread with the existing ID
            thread = AgentThread(service_thread_id=existing_thread_id)

            second_query = "What was the last city I asked about?"
            print(f"User: {second_query}")
            second_result = await agent.run(second_query, thread=thread)
            print(f"Agent: {second_result.text}")
            print("Note: The agent continues the conversation from the previous thread.\n")


async def main() -> None:
    print("=== Azure AI Chat Client Agent Thread Management Examples ===\n")

    await example_with_automatic_thread_creation()
    await example_with_thread_persistence()
    await example_with_existing_thread_id()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/README.md
================================================
# Azure OpenAI Agent Examples

This folder contains examples demonstrating different ways to create and use agents with the different Azure OpenAI chat client from the `agent_framework.azure` package.

## Examples

| File | Description |
|------|-------------|
| [`azure_assistants_basic.py`](azure_assistants_basic.py) | The simplest way to create an agent using `ChatAgent` with `AzureOpenAIAssistantsClient`. Shows both streaming and non-streaming responses with automatic assistant creation and cleanup. |
| [`azure_assistants_with_existing_assistant.py`](azure_assistants_with_existing_assistant.py) | Shows how to work with a pre-existing assistant by providing the assistant ID to the Azure Assistants client. Demonstrates proper cleanup of manually created assistants. |
| [`azure_assistants_with_explicit_settings.py`](azure_assistants_with_explicit_settings.py) | Shows how to initialize an agent with a specific assistants client, configuring settings explicitly including endpoint and deployment name. |
| [`azure_assistants_with_function_tools.py`](azure_assistants_with_function_tools.py) | Demonstrates how to use function tools with agents. Shows both agent-level tools (defined when creating the agent) and query-level tools (provided with specific queries). |
| [`azure_assistants_with_code_interpreter.py`](azure_assistants_with_code_interpreter.py) | Shows how to use the HostedCodeInterpreterTool with Azure agents to write and execute Python code. Includes helper methods for accessing code interpreter data from response chunks. |
| [`azure_assistants_with_thread.py`](azure_assistants_with_thread.py) | Demonstrates thread management with Azure agents, including automatic thread creation for stateless conversations and explicit thread management for maintaining conversation context across multiple interactions. |
| [`azure_chat_client_basic.py`](azure_chat_client_basic.py) | The simplest way to create an agent using `ChatAgent` with `AzureOpenAIChatClient`. Shows both streaming and non-streaming responses for chat-based interactions with Azure OpenAI models. |
| [`azure_chat_client_with_explicit_settings.py`](azure_chat_client_with_explicit_settings.py) | Shows how to initialize an agent with a specific chat client, configuring settings explicitly including endpoint and deployment name. |
| [`azure_chat_client_with_function_tools.py`](azure_chat_client_with_function_tools.py) | Demonstrates how to use function tools with agents. Shows both agent-level tools (defined when creating the agent) and query-level tools (provided with specific queries). |
| [`azure_chat_client_with_thread.py`](azure_chat_client_with_thread.py) | Demonstrates thread management with Azure agents, including automatic thread creation for stateless conversations and explicit thread management for maintaining conversation context across multiple interactions. |
| [`azure_responses_client_basic.py`](azure_responses_client_basic.py) | The simplest way to create an agent using `ChatAgent` with `AzureOpenAIResponsesClient`. Shows both streaming and non-streaming responses for structured response generation with Azure OpenAI models. |
| [`azure_responses_client_with_explicit_settings.py`](azure_responses_client_with_explicit_settings.py) | Shows how to initialize an agent with a specific responses client, configuring settings explicitly including endpoint and deployment name. |
| [`azure_responses_client_with_function_tools.py`](azure_responses_client_with_function_tools.py) | Demonstrates how to use function tools with agents. Shows both agent-level tools (defined when creating the agent) and query-level tools (provided with specific queries). |
| [`azure_responses_client_with_code_interpreter.py`](azure_responses_client_with_code_interpreter.py) | Shows how to use the HostedCodeInterpreterTool with Azure agents to write and execute Python code. Includes helper methods for accessing code interpreter data from response chunks. |
| [`azure_responses_client_with_thread.py`](azure_responses_client_with_thread.py) | Demonstrates thread management with Azure agents, including automatic thread creation for stateless conversations and explicit thread management for maintaining conversation context across multiple interactions. |
| [`azure_responses_client_image_analysis.py`](azure_responses_client_image_analysis.py) | Shows how to use Azure OpenAI Responses for image analysis and vision tasks. Demonstrates multi-modal messages combining text and image content using remote URLs. |

## Environment Variables

Make sure to set the following environment variables before running the examples:

- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`: The name of your Azure OpenAI chat model deployment
- `AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME`: The name of your Azure OpenAI Responses deployment

Optionally, you can set:
- `AZURE_OPENAI_API_VERSION`: The API version to use (default is `2024-02-15-preview`)
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key (if not using `AzureCliCredential`)
- `AZURE_OPENAI_BASE_URL`: Your Azure OpenAI base URL (if different from the endpoint)

## Authentication

All examples use `AzureCliCredential` for authentication. Run `az login` in your terminal before running the examples, or replace `AzureCliCredential` with your preferred authentication method.

## Required role-based access control (RBAC) roles

To access the Azure OpenAI API, your Azure account or service principal needs one of the following RBAC roles assigned to the Azure OpenAI resource:

- **Cognitive Services OpenAI User**: Provides read access to Azure OpenAI resources and the ability to call the inference APIs. This is the minimum role required for running these examples.
- **Cognitive Services OpenAI Contributor**: Provides full access to Azure OpenAI resources, including the ability to create, update, and delete deployments and models.

For most scenarios, the **Cognitive Services OpenAI User** role is sufficient. You can assign this role through the Azure portal under the Azure OpenAI resource's "Access control (IAM)" section.

For more detailed information about Azure OpenAI RBAC roles, see: [Role-based access control for Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/role-based-access-control)



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_assistants_basic.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.azure import AzureOpenAIAssistantsClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Assistants Basic Example

This sample demonstrates basic usage of AzureOpenAIAssistantsClient with automatic
assistant lifecycle management, showing both streaming and non-streaming responses.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    # Since no assistant ID is provided, the assistant will be automatically created
    # and deleted after getting a response
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with AzureOpenAIAssistantsClient(credential=AzureCliCredential()).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        query = "What's the weather like in Seattle?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    # Since no assistant ID is provided, the assistant will be automatically created
    # and deleted after getting a response
    async with AzureOpenAIAssistantsClient(credential=AzureCliCredential()).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        query = "What's the weather like in Portland?"
        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream(query):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")


async def main() -> None:
    print("=== Basic Azure OpenAI Assistants Chat Client Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_assistants_with_code_interpreter.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import AgentRunResponseUpdate, ChatAgent, ChatResponseUpdate, HostedCodeInterpreterTool
from agent_framework.azure import AzureOpenAIAssistantsClient
from azure.identity import AzureCliCredential
from openai.types.beta.threads.runs import (
    CodeInterpreterToolCallDelta,
    RunStepDelta,
    RunStepDeltaEvent,
    ToolCallDeltaObject,
)
from openai.types.beta.threads.runs.code_interpreter_tool_call_delta import CodeInterpreter

"""
Azure OpenAI Assistants with Code Interpreter Example

This sample demonstrates using HostedCodeInterpreterTool with Azure OpenAI Assistants
for Python code execution and mathematical problem solving.
"""


def get_code_interpreter_chunk(chunk: AgentRunResponseUpdate) -> str | None:
    """Helper method to access code interpreter data."""
    if (
        isinstance(chunk.raw_representation, ChatResponseUpdate)
        and isinstance(chunk.raw_representation.raw_representation, RunStepDeltaEvent)
        and isinstance(chunk.raw_representation.raw_representation.delta, RunStepDelta)
        and isinstance(chunk.raw_representation.raw_representation.delta.step_details, ToolCallDeltaObject)
        and chunk.raw_representation.raw_representation.delta.step_details.tool_calls
    ):
        for tool_call in chunk.raw_representation.raw_representation.delta.step_details.tool_calls:
            if (
                isinstance(tool_call, CodeInterpreterToolCallDelta)
                and isinstance(tool_call.code_interpreter, CodeInterpreter)
                and tool_call.code_interpreter.input is not None
            ):
                return tool_call.code_interpreter.input
    return None


async def main() -> None:
    """Example showing how to use the HostedCodeInterpreterTool with Azure OpenAI Assistants."""
    print("=== Azure OpenAI Assistants Agent with Code Interpreter Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with ChatAgent(
        chat_client=AzureOpenAIAssistantsClient(credential=AzureCliCredential()),
        instructions="You are a helpful assistant that can write and execute Python code to solve problems.",
        tools=HostedCodeInterpreterTool(),
    ) as agent:
        query = "What is current datetime?"
        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        generated_code = ""
        async for chunk in agent.run_stream(query):
            if chunk.text:
                print(chunk.text, end="", flush=True)
            code_interpreter_chunk = get_code_interpreter_chunk(chunk)
            if code_interpreter_chunk is not None:
                generated_code += code_interpreter_chunk

        print(f"\nGenerated code:\n{generated_code}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_assistants_with_existing_assistant.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIAssistantsClient
from azure.identity import AzureCliCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI
from pydantic import Field

"""
Azure OpenAI Assistants with Existing Assistant Example

This sample demonstrates working with pre-existing Azure OpenAI Assistants
using existing assistant IDs rather than creating new ones.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    print("=== Azure OpenAI Assistants Chat Client with Existing Assistant ===")

    token_provider = get_bearer_token_provider(AzureCliCredential(), "https://cognitiveservices.azure.com/.default")

    client = AsyncAzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_ad_token_provider=token_provider,
        api_version="2025-01-01-preview",
    )

    # Create an assistant that will persist
    created_assistant = await client.beta.assistants.create(
        model=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"], name="WeatherAssistant"
    )

    try:
        async with ChatAgent(
            chat_client=AzureOpenAIAssistantsClient(async_client=client, assistant_id=created_assistant.id),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent:
            result = await agent.run("What's the weather like in Tokyo?")
            print(f"Result: {result}\n")
    finally:
        # Clean up the assistant manually
        await client.beta.assistants.delete(created_assistant.id)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_assistants_with_explicit_settings.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework.azure import AzureOpenAIAssistantsClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Assistants with Explicit Settings Example

This sample demonstrates creating Azure OpenAI Assistants with explicit configuration
settings rather than relying on environment variable defaults.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    print("=== Azure Assistants Client with Explicit Settings ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with AzureOpenAIAssistantsClient(
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        deployment_name=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"],
        credential=AzureCliCredential(),
    ).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        result = await agent.run("What's the weather like in New York?")
        print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_assistants_with_function_tools.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from datetime import datetime, timezone
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIAssistantsClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Assistants with Function Tools Example

This sample demonstrates function tool integration with Azure OpenAI Assistants,
showing both agent-level and query-level tool configuration patterns.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with ChatAgent(
        chat_client=AzureOpenAIAssistantsClient(credential=AzureCliCredential()),
        instructions="You are a helpful assistant that can provide weather and time information.",
        tools=[get_weather, get_time],  # Tools defined at agent creation
    ) as agent:
        # First query - agent can use weather tool
        query1 = "What's the weather like in New York?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"Agent: {result1}\n")

        # Second query - agent can use time tool
        query2 = "What's the current UTC time?"
        print(f"User: {query2}")
        result2 = await agent.run(query2)
        print(f"Agent: {result2}\n")

        # Third query - agent can use both tools if needed
        query3 = "What's the weather in London and what's the current UTC time?"
        print(f"User: {query3}")
        result3 = await agent.run(query3)
        print(f"Agent: {result3}\n")


async def tools_on_run_level() -> None:
    """Example showing tools passed to the run method."""
    print("=== Tools Passed to Run Method ===")

    # Agent created without tools
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with ChatAgent(
        chat_client=AzureOpenAIAssistantsClient(credential=AzureCliCredential()),
        instructions="You are a helpful assistant.",
        # No tools defined here
    ) as agent:
        # First query with weather tool
        query1 = "What's the weather like in Seattle?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, tools=[get_weather])  # Tool passed to run method
        print(f"Agent: {result1}\n")

        # Second query with time tool
        query2 = "What's the current UTC time?"
        print(f"User: {query2}")
        result2 = await agent.run(query2, tools=[get_time])  # Different tool for this query
        print(f"Agent: {result2}\n")

        # Third query with multiple tools
        query3 = "What's the weather in Chicago and what's the current UTC time?"
        print(f"User: {query3}")
        result3 = await agent.run(query3, tools=[get_weather, get_time])  # Multiple tools
        print(f"Agent: {result3}\n")


async def mixed_tools_example() -> None:
    """Example showing both agent-level tools and run-method tools."""
    print("=== Mixed Tools Example (Agent + Run Method) ===")

    # Agent created with some base tools
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with ChatAgent(
        chat_client=AzureOpenAIAssistantsClient(credential=AzureCliCredential()),
        instructions="You are a comprehensive assistant that can help with various information requests.",
        tools=[get_weather],  # Base tool available for all queries
    ) as agent:
        # Query using both agent tool and additional run-method tools
        query = "What's the weather in Denver and what's the current UTC time?"
        print(f"User: {query}")

        # Agent has access to get_weather (from creation) + additional tools from run method
        result = await agent.run(
            query,
            tools=[get_time],  # Additional tools for this specific query
        )
        print(f"Agent: {result}\n")


async def main() -> None:
    print("=== Azure OpenAI Assistants Chat Client Agent with Function Tools Examples ===\n")

    await tools_on_agent_level()
    await tools_on_run_level()
    await mixed_tools_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_assistants_with_thread.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework import AgentThread, ChatAgent
from agent_framework.azure import AzureOpenAIAssistantsClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Assistants with Thread Management Example

This sample demonstrates thread management with Azure OpenAI Assistants, comparing
automatic thread creation with explicit thread management for persistent context.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def example_with_automatic_thread_creation() -> None:
    """Example showing automatic thread creation (service-managed thread)."""
    print("=== Automatic Thread Creation Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with ChatAgent(
        chat_client=AzureOpenAIAssistantsClient(credential=AzureCliCredential()),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        # First conversation - no thread provided, will be created automatically
        query1 = "What's the weather like in Seattle?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"Agent: {result1.text}")

        # Second conversation - still no thread provided, will create another new thread
        query2 = "What was the last city I asked about?"
        print(f"\nUser: {query2}")
        result2 = await agent.run(query2)
        print(f"Agent: {result2.text}")
        print("Note: Each call creates a separate thread, so the agent doesn't remember previous context.\n")


async def example_with_thread_persistence() -> None:
    """Example showing thread persistence across multiple conversations."""
    print("=== Thread Persistence Example ===")
    print("Using the same thread across multiple conversations to maintain context.\n")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with ChatAgent(
        chat_client=AzureOpenAIAssistantsClient(credential=AzureCliCredential()),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        # Create a new thread that will be reused
        thread = agent.get_new_thread()

        # First conversation
        query1 = "What's the weather like in Tokyo?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, thread=thread)
        print(f"Agent: {result1.text}")

        # Second conversation using the same thread - maintains context
        query2 = "How about London?"
        print(f"\nUser: {query2}")
        result2 = await agent.run(query2, thread=thread)
        print(f"Agent: {result2.text}")

        # Third conversation - agent should remember both previous cities
        query3 = "Which of the cities I asked about has better weather?"
        print(f"\nUser: {query3}")
        result3 = await agent.run(query3, thread=thread)
        print(f"Agent: {result3.text}")
        print("Note: The agent remembers context from previous messages in the same thread.\n")


async def example_with_existing_thread_id() -> None:
    """Example showing how to work with an existing thread ID from the service."""
    print("=== Existing Thread ID Example ===")
    print("Using a specific thread ID to continue an existing conversation.\n")

    # First, create a conversation and capture the thread ID
    existing_thread_id = None

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with ChatAgent(
        chat_client=AzureOpenAIAssistantsClient(credential=AzureCliCredential()),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        # Start a conversation and get the thread ID
        thread = agent.get_new_thread()
        query1 = "What's the weather in Paris?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, thread=thread)
        print(f"Agent: {result1.text}")

        # The thread ID is set after the first response
        existing_thread_id = thread.service_thread_id
        print(f"Thread ID: {existing_thread_id}")

    if existing_thread_id:
        print("\n--- Continuing with the same thread ID in a new agent instance ---")

        # Create a new agent instance but use the existing thread ID
        async with ChatAgent(
            chat_client=AzureOpenAIAssistantsClient(thread_id=existing_thread_id, credential=AzureCliCredential()),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent:
            # Create a thread with the existing ID
            thread = AgentThread(service_thread_id=existing_thread_id)

            query2 = "What was the last city I asked about?"
            print(f"User: {query2}")
            result2 = await agent.run(query2, thread=thread)
            print(f"Agent: {result2.text}")
            print("Note: The agent continues the conversation from the previous thread.\n")


async def main() -> None:
    print("=== Azure OpenAI Assistants Chat Client Agent Thread Management Examples ===\n")

    await example_with_automatic_thread_creation()
    await example_with_thread_persistence()
    await example_with_existing_thread_id()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_chat_client_basic.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Chat Client Basic Example

This sample demonstrates basic usage of AzureOpenAIChatClient for direct chat-based
interactions, showing both streaming and non-streaming responses.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    # Create agent with Azure Chat Client
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = AzureOpenAIChatClient(credential=AzureCliCredential()).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Seattle?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Result: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    # Create agent with Azure Chat Client
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = AzureOpenAIChatClient(credential=AzureCliCredential()).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Portland?"
    print(f"User: {query}")
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run_stream(query):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


async def main() -> None:
    print("=== Basic Azure Chat Client Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_chat_client_with_explicit_settings.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Chat Client with Explicit Settings Example

This sample demonstrates creating Azure OpenAI Chat Client with explicit configuration
settings rather than relying on environment variable defaults.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    print("=== Azure Chat Client with Explicit Settings ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = AzureOpenAIChatClient(
        deployment_name=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"],
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        credential=AzureCliCredential(),
    ).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    result = await agent.run("What's the weather like in New York?")
    print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_chat_client_with_function_tools.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from datetime import datetime, timezone
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Chat Client with Function Tools Example

This sample demonstrates function tool integration with Azure OpenAI Chat Client,
showing both agent-level and query-level tool configuration patterns.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIChatClient(credential=AzureCliCredential()),
        instructions="You are a helpful assistant that can provide weather and time information.",
        tools=[get_weather, get_time],  # Tools defined at agent creation
    )

    # First query - agent can use weather tool
    query1 = "What's the weather like in New York?"
    print(f"User: {query1}")
    result1 = await agent.run(query1)
    print(f"Agent: {result1}\n")

    # Second query - agent can use time tool
    query2 = "What's the current UTC time?"
    print(f"User: {query2}")
    result2 = await agent.run(query2)
    print(f"Agent: {result2}\n")

    # Third query - agent can use both tools if needed
    query3 = "What's the weather in London and what's the current UTC time?"
    print(f"User: {query3}")
    result3 = await agent.run(query3)
    print(f"Agent: {result3}\n")


async def tools_on_run_level() -> None:
    """Example showing tools passed to the run method."""
    print("=== Tools Passed to Run Method ===")

    # Agent created without tools
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIChatClient(credential=AzureCliCredential()),
        instructions="You are a helpful assistant.",
        # No tools defined here
    )

    # First query with weather tool
    query1 = "What's the weather like in Seattle?"
    print(f"User: {query1}")
    result1 = await agent.run(query1, tools=[get_weather])  # Tool passed to run method
    print(f"Agent: {result1}\n")

    # Second query with time tool
    query2 = "What's the current UTC time?"
    print(f"User: {query2}")
    result2 = await agent.run(query2, tools=[get_time])  # Different tool for this query
    print(f"Agent: {result2}\n")

    # Third query with multiple tools
    query3 = "What's the weather in Chicago and what's the current UTC time?"
    print(f"User: {query3}")
    result3 = await agent.run(query3, tools=[get_weather, get_time])  # Multiple tools
    print(f"Agent: {result3}\n")


async def mixed_tools_example() -> None:
    """Example showing both agent-level tools and run-method tools."""
    print("=== Mixed Tools Example (Agent + Run Method) ===")

    # Agent created with some base tools
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIChatClient(credential=AzureCliCredential()),
        instructions="You are a comprehensive assistant that can help with various information requests.",
        tools=[get_weather],  # Base tool available for all queries
    )

    # Query using both agent tool and additional run-method tools
    query = "What's the weather in Denver and what's the current UTC time?"
    print(f"User: {query}")

    # Agent has access to get_weather (from creation) + additional tools from run method
    result = await agent.run(
        query,
        tools=[get_time],  # Additional tools for this specific query
    )
    print(f"Agent: {result}\n")


async def main() -> None:
    print("=== Azure Chat Client Agent with Function Tools Examples ===\n")

    await tools_on_agent_level()
    await tools_on_run_level()
    await mixed_tools_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_chat_client_with_thread.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework import AgentThread, ChatAgent, ChatMessageStore
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Chat Client with Thread Management Example

This sample demonstrates thread management with Azure OpenAI Chat Client, comparing
automatic thread creation with explicit thread management for persistent context.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def example_with_automatic_thread_creation() -> None:
    """Example showing automatic thread creation (service-managed thread)."""
    print("=== Automatic Thread Creation Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIChatClient(credential=AzureCliCredential()),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # First conversation - no thread provided, will be created automatically
    query1 = "What's the weather like in Seattle?"
    print(f"User: {query1}")
    result1 = await agent.run(query1)
    print(f"Agent: {result1.text}")

    # Second conversation - still no thread provided, will create another new thread
    query2 = "What was the last city I asked about?"
    print(f"\nUser: {query2}")
    result2 = await agent.run(query2)
    print(f"Agent: {result2.text}")
    print("Note: Each call creates a separate thread, so the agent doesn't remember previous context.\n")


async def example_with_thread_persistence() -> None:
    """Example showing thread persistence across multiple conversations."""
    print("=== Thread Persistence Example ===")
    print("Using the same thread across multiple conversations to maintain context.\n")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIChatClient(credential=AzureCliCredential()),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # Create a new thread that will be reused
    thread = agent.get_new_thread()

    # First conversation
    query1 = "What's the weather like in Tokyo?"
    print(f"User: {query1}")
    result1 = await agent.run(query1, thread=thread)
    print(f"Agent: {result1.text}")

    # Second conversation using the same thread - maintains context
    query2 = "How about London?"
    print(f"\nUser: {query2}")
    result2 = await agent.run(query2, thread=thread)
    print(f"Agent: {result2.text}")

    # Third conversation - agent should remember both previous cities
    query3 = "Which of the cities I asked about has better weather?"
    print(f"\nUser: {query3}")
    result3 = await agent.run(query3, thread=thread)
    print(f"Agent: {result3.text}")
    print("Note: The agent remembers context from previous messages in the same thread.\n")


async def example_with_existing_thread_messages() -> None:
    """Example showing how to work with existing thread messages for Azure."""
    print("=== Existing Thread Messages Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIChatClient(credential=AzureCliCredential()),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # Start a conversation and build up message history
    thread = agent.get_new_thread()

    query1 = "What's the weather in Paris?"
    print(f"User: {query1}")
    result1 = await agent.run(query1, thread=thread)
    print(f"Agent: {result1.text}")

    # The thread now contains the conversation history in memory
    if thread.message_store:
        messages = await thread.message_store.list_messages()
        print(f"Thread contains {len(messages or [])} messages")

    print("\n--- Continuing with the same thread in a new agent instance ---")

    # Create a new agent instance but use the existing thread with its message history
    new_agent = ChatAgent(
        chat_client=AzureOpenAIChatClient(credential=AzureCliCredential()),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # Use the same thread object which contains the conversation history
    query2 = "What was the last city I asked about?"
    print(f"User: {query2}")
    result2 = await new_agent.run(query2, thread=thread)
    print(f"Agent: {result2.text}")
    print("Note: The agent continues the conversation using the local message history.\n")

    print("\n--- Alternative: Creating a new thread from existing messages ---")

    # You can also create a new thread from existing messages
    messages = await thread.message_store.list_messages() if thread.message_store else []
    new_thread = AgentThread(message_store=ChatMessageStore(messages))

    query3 = "How does the Paris weather compare to London?"
    print(f"User: {query3}")
    result3 = await new_agent.run(query3, thread=new_thread)
    print(f"Agent: {result3.text}")
    print("Note: This creates a new thread with the same conversation history.\n")


async def main() -> None:
    print("=== Azure Chat Client Agent Thread Management Examples ===\n")

    await example_with_automatic_thread_creation()
    await example_with_thread_persistence()
    await example_with_existing_thread_messages()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_responses_client_basic.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Responses Client Basic Example

This sample demonstrates basic usage of AzureOpenAIResponsesClient for structured
response generation, showing both streaming and non-streaming responses.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = AzureOpenAIResponsesClient(credential=AzureCliCredential()).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Seattle?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Result: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = AzureOpenAIResponsesClient(credential=AzureCliCredential()).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Portland?"
    print(f"User: {query}")
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run_stream(query):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


async def main() -> None:
    print("=== Basic Azure OpenAI Responses Client Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_responses_client_code_interpreter_files.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
import tempfile

from agent_framework import ChatAgent, HostedCodeInterpreterTool
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from openai import AsyncAzureOpenAI

"""
Azure OpenAI Responses Client with Code Interpreter and Files Example

This sample demonstrates using HostedCodeInterpreterTool with Azure OpenAI Responses
for Python code execution and data analysis with uploaded files.
"""

# Helper functions


async def create_sample_file_and_upload(openai_client: AsyncAzureOpenAI) -> tuple[str, str]:
    """Create a sample CSV file and upload it to Azure OpenAI."""
    csv_data = """name,department,salary,years_experience
Alice Johnson,Engineering,95000,5
Bob Smith,Sales,75000,3
Carol Williams,Engineering,105000,8
David Brown,Marketing,68000,2
Emma Davis,Sales,82000,4
Frank Wilson,Engineering,88000,6
"""

    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as temp_file:
        temp_file.write(csv_data)
        temp_file_path = temp_file.name

    # Upload file to Azure OpenAI
    print("Uploading file to Azure OpenAI...")
    with open(temp_file_path, "rb") as file:
        uploaded_file = await openai_client.files.create(
            file=file,
            purpose="assistants",  # Required for code interpreter
        )

    print(f"File uploaded with ID: {uploaded_file.id}")
    return temp_file_path, uploaded_file.id


async def cleanup_files(openai_client: AsyncAzureOpenAI, temp_file_path: str, file_id: str) -> None:
    """Clean up both local temporary file and uploaded file."""
    # Clean up: delete the uploaded file
    await openai_client.files.delete(file_id)
    print(f"Cleaned up uploaded file: {file_id}")

    # Clean up temporary local file
    os.unlink(temp_file_path)
    print(f"Cleaned up temporary file: {temp_file_path}")


async def main() -> None:
    print("=== Azure OpenAI Code Interpreter with File Upload ===")

    # Initialize Azure OpenAI client for file operations
    credential = AzureCliCredential()

    async def get_token():
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        return token.token

    openai_client = AsyncAzureOpenAI(
        azure_ad_token_provider=get_token,
        api_version="2024-05-01-preview",
    )

    temp_file_path, file_id = await create_sample_file_and_upload(openai_client)

    # Create agent using Azure OpenAI Responses client
    agent = ChatAgent(
        chat_client=AzureOpenAIResponsesClient(credential=credential),
        instructions="You are a helpful assistant that can analyze data files using Python code.",
        tools=HostedCodeInterpreterTool(inputs=[{"file_id": file_id}]),
    )

    # Test the code interpreter with the uploaded file
    query = "Analyze the employee data in the uploaded CSV file. Calculate average salary by department."
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Agent: {result.text}")

    await cleanup_files(openai_client, temp_file_path, file_id)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_responses_client_image_analysis.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import ChatMessage, TextContent, UriContent
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

"""
Azure OpenAI Responses Client with Image Analysis Example

This sample demonstrates using Azure OpenAI Responses for image analysis and vision tasks,
showing multi-modal messages combining text and image content.
"""


async def main():
    print("=== Azure Responses Agent with Image Analysis ===")

    # 1. Create an Azure Responses agent with vision capabilities
    agent = AzureOpenAIResponsesClient(credential=AzureCliCredential()).create_agent(
        name="VisionAgent",
        instructions="You are a helpful agent that can analyze images.",
    )

    # 2. Create a simple message with both text and image content
    user_message = ChatMessage(
        role="user",
        contents=[
            TextContent(text="What do you see in this image?"),
            UriContent(
                uri="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                media_type="image/jpeg",
            ),
        ],
    )

    # 3. Get the agent's response
    print("User: What do you see in this image? [Image provided]")
    result = await agent.run(user_message)
    print(f"Agent: {result.text}")
    print()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_responses_client_with_code_interpreter.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import ChatAgent, ChatResponse, HostedCodeInterpreterTool
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from openai.types.responses.response import Response as OpenAIResponse
from openai.types.responses.response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall

"""
Azure OpenAI Responses Client with Code Interpreter Example

This sample demonstrates using HostedCodeInterpreterTool with Azure OpenAI Responses
for Python code execution and mathematical problem solving.
"""


async def main() -> None:
    """Example showing how to use the HostedCodeInterpreterTool with Azure OpenAI Responses."""
    print("=== Azure OpenAI Responses Agent with Code Interpreter Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIResponsesClient(credential=AzureCliCredential()),
        instructions="You are a helpful assistant that can write and execute Python code to solve problems.",
        tools=HostedCodeInterpreterTool(),
    )

    query = "Use code to calculate the factorial of 100?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Result: {result}\n")

    if (
        isinstance(result.raw_representation, ChatResponse)
        and isinstance(result.raw_representation.raw_representation, OpenAIResponse)
        and len(result.raw_representation.raw_representation.output) > 0
        and isinstance(result.raw_representation.raw_representation.output[0], ResponseCodeInterpreterToolCall)
    ):
        generated_code = result.raw_representation.raw_representation.output[0].code

        print(f"Generated code:\n{generated_code}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_responses_client_with_explicit_settings.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Responses Client with Explicit Settings Example

This sample demonstrates creating Azure OpenAI Responses Client with explicit configuration
settings rather than relying on environment variable defaults.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    print("=== Azure Responses Client with Explicit Settings ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = AzureOpenAIResponsesClient(
        deployment_name=os.environ["AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"],
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        credential=AzureCliCredential(),
    ).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    result = await agent.run("What's the weather like in New York?")
    print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_responses_client_with_function_tools.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from datetime import datetime, timezone
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Responses Client with Function Tools Example

This sample demonstrates function tool integration with Azure OpenAI Responses Client,
showing both agent-level and query-level tool configuration patterns.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIResponsesClient(credential=AzureCliCredential()),
        instructions="You are a helpful assistant that can provide weather and time information.",
        tools=[get_weather, get_time],  # Tools defined at agent creation
    )

    # First query - agent can use weather tool
    query1 = "What's the weather like in New York?"
    print(f"User: {query1}")
    result1 = await agent.run(query1)
    print(f"Agent: {result1}\n")

    # Second query - agent can use time tool
    query2 = "What's the current UTC time?"
    print(f"User: {query2}")
    result2 = await agent.run(query2)
    print(f"Agent: {result2}\n")

    # Third query - agent can use both tools if needed
    query3 = "What's the weather in London and what's the current UTC time?"
    print(f"User: {query3}")
    result3 = await agent.run(query3)
    print(f"Agent: {result3}\n")


async def tools_on_run_level() -> None:
    """Example showing tools passed to the run method."""
    print("=== Tools Passed to Run Method ===")

    # Agent created without tools
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIResponsesClient(credential=AzureCliCredential()),
        instructions="You are a helpful assistant.",
        # No tools defined here
    )

    # First query with weather tool
    query1 = "What's the weather like in Seattle?"
    print(f"User: {query1}")
    result1 = await agent.run(query1, tools=[get_weather])  # Tool passed to run method
    print(f"Agent: {result1}\n")

    # Second query with time tool
    query2 = "What's the current UTC time?"
    print(f"User: {query2}")
    result2 = await agent.run(query2, tools=[get_time])  # Different tool for this query
    print(f"Agent: {result2}\n")

    # Third query with multiple tools
    query3 = "What's the weather in Chicago and what's the current UTC time?"
    print(f"User: {query3}")
    result3 = await agent.run(query3, tools=[get_weather, get_time])  # Multiple tools
    print(f"Agent: {result3}\n")


async def mixed_tools_example() -> None:
    """Example showing both agent-level tools and run-method tools."""
    print("=== Mixed Tools Example (Agent + Run Method) ===")

    # Agent created with some base tools
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIResponsesClient(credential=AzureCliCredential()),
        instructions="You are a comprehensive assistant that can help with various information requests.",
        tools=[get_weather],  # Base tool available for all queries
    )

    # Query using both agent tool and additional run-method tools
    query = "What's the weather in Denver and what's the current UTC time?"
    print(f"User: {query}")

    # Agent has access to get_weather (from creation) + additional tools from run method
    result = await agent.run(
        query,
        tools=[get_time],  # Additional tools for this specific query
    )
    print(f"Agent: {result}\n")


async def main() -> None:
    print("=== Azure OpenAI Responses Client Agent with Function Tools Examples ===\n")

    await tools_on_agent_level()
    await tools_on_run_level()
    await mixed_tools_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_responses_client_with_local_mcp.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import os
import asyncio

from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential

"""
Azure OpenAI Responses Client with local Model Context Protocol (MCP) Example

This sample demonstrates integration of Azure OpenAI Responses Client with local Model Context Protocol (MCP)
servers.
"""


# --- Below code uses Microsoft Learn MCP server over Streamable HTTP ---
# --- Users can set these environment variables, or just edit the values below to their desired local MCP server
MCP_NAME = os.environ.get("MCP_NAME", "Microsoft Learn MCP")  # example name
MCP_URL = os.environ.get("MCP_URL", "https://learn.microsoft.com/api/mcp")   # example endpoint

# Environment variables for Azure OpenAI Responses authentication
# AZURE_OPENAI_ENDPOINT="<your-azure openai-endpoint>"
# AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME="<your-deployment-name>"
# AZURE_OPENAI_API_VERSION="<your-api-version>"  # e.g. "2025-03-01-preview"

async def main():
    """Example showing local MCP tools for a Azure OpenAI Responses Agent."""
    # AuthN: use Azure CLI
    credential = AzureCliCredential()

    # Build an agent backed by Azure OpenAI Responses
    # (endpoint/deployment/api_version can also come from env vars above)
    responses_client = AzureOpenAIResponsesClient(
        credential=credential,
    )

    agent: ChatAgent = responses_client.create_agent(
        name="DocsAgent",
        instructions=(
            "You are a helpful assistant that can help with Microsoft documentation questions."
        ),
    )

    # Connect to the MCP server (Streamable HTTP)
    async with MCPStreamableHTTPTool(
        name=MCP_NAME,
        url=MCP_URL,
        
    ) as mcp_tool:
        # First query — expect the agent to use the MCP tool if it helps
        q1 = "How to create an Azure storage account using az cli?"
        r1 = await agent.run(q1, tools=mcp_tool)
        print("\n=== Answer 1 ===\n", r1.text)

        # Follow-up query (connection is reused)
        q2 = "What is Microsoft Agent Framework?"
        r2 = await agent.run(q2, tools=mcp_tool)
        print("\n=== Answer 2 ===\n", r2.text)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/azure_openai/azure_responses_client_with_thread.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework import AgentThread, ChatAgent
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure OpenAI Responses Client with Thread Management Example

This sample demonstrates thread management with Azure OpenAI Responses Client, comparing
automatic thread creation with explicit thread management for persistent context.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def example_with_automatic_thread_creation() -> None:
    """Example showing automatic thread creation."""
    print("=== Automatic Thread Creation Example ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIResponsesClient(credential=AzureCliCredential()),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # First conversation - no thread provided, will be created automatically
    query1 = "What's the weather like in Seattle?"
    print(f"User: {query1}")
    result1 = await agent.run(query1)
    print(f"Agent: {result1.text}")

    # Second conversation - still no thread provided, will create another new thread
    query2 = "What was the last city I asked about?"
    print(f"\nUser: {query2}")
    result2 = await agent.run(query2)
    print(f"Agent: {result2.text}")
    print("Note: Each call creates a separate thread, so the agent doesn't remember previous context.\n")


async def example_with_thread_persistence_in_memory() -> None:
    """
    Example showing thread persistence across multiple conversations.
    In this example, messages are stored in-memory.
    """
    print("=== Thread Persistence Example (In-Memory) ===")

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIResponsesClient(credential=AzureCliCredential()),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # Create a new thread that will be reused
    thread = agent.get_new_thread()

    # First conversation
    query1 = "What's the weather like in Tokyo?"
    print(f"User: {query1}")
    result1 = await agent.run(query1, thread=thread)
    print(f"Agent: {result1.text}")

    # Second conversation using the same thread - maintains context
    query2 = "How about London?"
    print(f"\nUser: {query2}")
    result2 = await agent.run(query2, thread=thread)
    print(f"Agent: {result2.text}")

    # Third conversation - agent should remember both previous cities
    query3 = "Which of the cities I asked about has better weather?"
    print(f"\nUser: {query3}")
    result3 = await agent.run(query3, thread=thread)
    print(f"Agent: {result3.text}")
    print("Note: The agent remembers context from previous messages in the same thread.\n")


async def example_with_existing_thread_id() -> None:
    """
    Example showing how to work with an existing thread ID from the service.
    In this example, messages are stored on the server using Azure OpenAI conversation state.
    """
    print("=== Existing Thread ID Example ===")

    # First, create a conversation and capture the thread ID
    existing_thread_id = None

    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    agent = ChatAgent(
        chat_client=AzureOpenAIResponsesClient(credential=AzureCliCredential()),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # Start a conversation and get the thread ID
    thread = agent.get_new_thread()

    query1 = "What's the weather in Paris?"
    print(f"User: {query1}")
    # Enable Azure OpenAI conversation state by setting `store` parameter to True
    result1 = await agent.run(query1, thread=thread, store=True)
    print(f"Agent: {result1.text}")

    # The thread ID is set after the first response
    existing_thread_id = thread.service_thread_id
    print(f"Thread ID: {existing_thread_id}")

    if existing_thread_id:
        print("\n--- Continuing with the same thread ID in a new agent instance ---")

        agent = ChatAgent(
            chat_client=AzureOpenAIResponsesClient(credential=AzureCliCredential()),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        )

        # Create a thread with the existing ID
        thread = AgentThread(service_thread_id=existing_thread_id)

        query2 = "What was the last city I asked about?"
        print(f"User: {query2}")
        result2 = await agent.run(query2, thread=thread, store=True)
        print(f"Agent: {result2.text}")
        print("Note: The agent continues the conversation from the previous thread by using thread ID.\n")


async def main() -> None:
    print("=== Azure OpenAI Response Client Agent Thread Management Examples ===\n")

    await example_with_automatic_thread_creation()
    await example_with_thread_persistence_in_memory()
    await example_with_existing_thread_id()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/copilotstudio/README.md
================================================
# Copilot Studio Agent Examples

This folder contains examples demonstrating how to create and use agents with Microsoft Copilot Studio using the Agent Framework.

## Prerequisites

Before running these examples, you need:

1. **Copilot Studio Environment**: Access to a Microsoft Copilot Studio environment with a published copilot
2. **App Registration**: An Azure AD App Registration with appropriate permissions
3. **Environment Variables**: Set the following environment variables:
   - `COPILOTSTUDIOAGENT__ENVIRONMENTID` - Your Copilot Studio environment ID
   - `COPILOTSTUDIOAGENT__SCHEMANAME` - Your copilot's agent identifier/schema name
   - `COPILOTSTUDIOAGENT__AGENTAPPID` - Your App Registration client ID
   - `COPILOTSTUDIOAGENT__TENANTID` - Your Azure AD tenant ID

## Examples

| Example | Description |
|---------|-------------|
| **[`copilotstudio_basic.py`](copilotstudio_basic.py)** | Basic non-streaming and streaming execution with simple questions |
| **[`copilotstudio_with_explicit_settings.py`](copilotstudio_with_explicit_settings.py)** | Example with explicit settings and manual token acquisition |

## Authentication

The examples use MSAL (Microsoft Authentication Library) for authentication. The first time you run an example, you may need to complete an interactive authentication flow in your browser.

### App Registration Setup

Your Azure AD App Registration should have:

1. **API Permissions**:
   - Power Platform API permissions (https://api.powerplatform.com/.default)
   - Appropriate delegated permissions for your organization

2. **Redirect URIs**:
   - For public client flows: `http://localhost`
   - Configure as appropriate for your authentication method

3. **Authentication**:
   - Enable "Allow public client flows" if using interactive authentication

## Usage Patterns

### Basic Usage with Environment Variables

```python
import asyncio
from agent_framework.microsoft import CopilotStudioAgent

# Uses environment variables for configuration
async def main():
    # Create agent using environment variables
    agent = CopilotStudioAgent()

    # Run a simple query
    result = await agent.run("What is the capital of France?")
    print(result)

asyncio.run(main())
```

### Explicit Configuration

```python
from agent_framework.microsoft import CopilotStudioAgent, acquire_token
from microsoft_agents.copilotstudio.client import ConnectionSettings, CopilotClient, PowerPlatformCloud, AgentType

# Acquire token manually
token = acquire_token(
    client_id="your-client-id",
    tenant_id="your-tenant-id"
)

# Create settings and client
settings = ConnectionSettings(
    environment_id="your-environment-id",
    agent_identifier="your-agent-schema-name",
    cloud=PowerPlatformCloud.PROD,
    copilot_agent_type=AgentType.PUBLISHED,
    custom_power_platform_cloud=None
)

client = CopilotClient(settings=settings, token=token)
agent = CopilotStudioAgent(client=client)
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify your App Registration has correct permissions
   - Ensure environment variables are set correctly
   - Check that your tenant ID and client ID are valid

2. **Environment/Agent Not Found**:
   - Verify your environment ID is correct
   - Ensure your copilot is published and the schema name is correct
   - Check that you have access to the specified environment

3. **Token Acquisition Failures**:
   - Interactive authentication may require browser access
   - Corporate firewalls may block authentication flows
   - Try running with appropriate proxy settings if needed



================================================
FILE: python/samples/getting_started/agents/copilotstudio/copilotstudio_basic.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework.microsoft import CopilotStudioAgent

"""
Copilot Studio Agent Basic Example

This sample demonstrates basic usage of CopilotStudioAgent with automatic configuration
from environment variables, showing both streaming and non-streaming responses.
"""

# Environment variables needed:
# COPILOTSTUDIOAGENT__ENVIRONMENTID - Environment ID where your copilot is deployed
# COPILOTSTUDIOAGENT__SCHEMANAME - Agent identifier/schema name of your copilot
# COPILOTSTUDIOAGENT__AGENTAPPID - Client ID for authentication
# COPILOTSTUDIOAGENT__TENANTID - Tenant ID for authentication


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    agent = CopilotStudioAgent()

    query = "What is the capital of France?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Agent: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    agent = CopilotStudioAgent()

    query = "What is the capital of Spain?"
    print(f"User: {query}")
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run_stream(query):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


async def main() -> None:
    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/copilotstudio/copilotstudio_with_explicit_settings.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from agent_framework.microsoft import CopilotStudioAgent, acquire_token
from microsoft_agents.copilotstudio.client import AgentType, ConnectionSettings, CopilotClient, PowerPlatformCloud

"""
Copilot Studio Agent with Explicit Settings Example

This sample demonstrates explicit configuration of CopilotStudioAgent with manual
token management and custom ConnectionSettings for production environments.
"""

# Environment variables needed:
# COPILOTSTUDIOAGENT__ENVIRONMENTID - Environment ID where your copilot is deployed
# COPILOTSTUDIOAGENT__SCHEMANAME - Agent identifier/schema name of your copilot
# COPILOTSTUDIOAGENT__AGENTAPPID - Client ID for authentication
# COPILOTSTUDIOAGENT__TENANTID - Tenant ID for authentication


async def example_with_connection_settings() -> None:
    """Example using explicit ConnectionSettings and CopilotClient."""
    print("=== Copilot Studio Agent with Connection Settings ===")

    # Configuration from environment variables
    environment_id = os.environ["COPILOTSTUDIOAGENT__ENVIRONMENTID"]
    agent_identifier = os.environ["COPILOTSTUDIOAGENT__SCHEMANAME"]
    client_id = os.environ["COPILOTSTUDIOAGENT__AGENTAPPID"]
    tenant_id = os.environ["COPILOTSTUDIOAGENT__TENANTID"]

    # Acquire token using the acquire_token function
    token = acquire_token(
        client_id=client_id,
        tenant_id=tenant_id,
    )

    # Create connection settings
    settings = ConnectionSettings(
        environment_id=environment_id,
        agent_identifier=agent_identifier,
        cloud=PowerPlatformCloud.PROD,  # Or PowerPlatformCloud.GOV, PowerPlatformCloud.HIGH, etc.
        copilot_agent_type=AgentType.PUBLISHED,  # Or AgentType.PREBUILT
        custom_power_platform_cloud=None,  # Optional: for custom cloud endpoints
    )

    # Create CopilotClient with explicit settings
    client = CopilotClient(settings=settings, token=token)

    # Create agent with explicit client
    agent = CopilotStudioAgent(client=client)

    # Run a simple query
    query = "What is the capital of Italy?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Agent: {result}")


async def example_with_explicit_parameters() -> None:
    """Example using CopilotStudioAgent with all parameters explicitly provided."""
    print("\n=== Copilot Studio Agent with All Explicit Parameters ===")

    # Configuration from environment variables
    environment_id = os.environ["COPILOTSTUDIOAGENT__ENVIRONMENTID"]
    agent_identifier = os.environ["COPILOTSTUDIOAGENT__SCHEMANAME"]
    client_id = os.environ["COPILOTSTUDIOAGENT__AGENTAPPID"]
    tenant_id = os.environ["COPILOTSTUDIOAGENT__TENANTID"]

    # Create agent with all parameters explicitly
    agent = CopilotStudioAgent(
        environment_id=environment_id,
        agent_identifier=agent_identifier,
        client_id=client_id,
        tenant_id=tenant_id,
        cloud=PowerPlatformCloud.PROD,
        agent_type=AgentType.PUBLISHED,
    )

    # Run a simple query
    query = "What is the capital of Japan?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Agent: {result}")


async def main() -> None:
    await example_with_connection_settings()
    await example_with_explicit_parameters()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/custom/README.md
================================================
# Custom Agent and Chat Client Examples

This folder contains examples demonstrating how to implement custom agents and chat clients using the Microsoft Agent Framework.

## Examples

| File | Description |
|------|-------------|
| [`custom_agent.py`](custom_agent.py) | Shows how to create custom agents by extending the `BaseAgent` class. Demonstrates the `EchoAgent` implementation with both streaming and non-streaming responses, proper thread management, and message history handling. |
| [`custom_chat_client.py`](custom_chat_client.py) | Demonstrates how to create custom chat clients by extending the `BaseChatClient` class. Shows the `EchoingChatClient` implementation and how to integrate it with `ChatAgent` using the `create_agent()` method. |

## Key Takeaways

### Custom Agents
- Custom agents give you complete control over the agent's behavior
- You must implement both `run()` (for complete responses) and `run_stream()` (for streaming responses)
- Use `self._normalize_messages()` to handle different input message formats
- Use `self._notify_thread_of_new_messages()` to properly manage conversation history

### Custom Chat Clients
- Custom chat clients allow you to integrate any backend service or create new LLM providers
- You must implement both `_inner_get_response()` and `_inner_get_streaming_response()`
- Custom chat clients can be used with `ChatAgent` to leverage all agent framework features
- Use the `create_agent()` method to easily create agents from your custom chat clients

Both approaches allow you to extend the framework for your specific use cases while maintaining compatibility with the broader Agent Framework ecosystem.


================================================
FILE: python/samples/getting_started/agents/custom/custom_agent.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from collections.abc import AsyncIterable
from typing import Any

from agent_framework import (
    AgentRunResponse,
    AgentRunResponseUpdate,
    AgentThread,
    BaseAgent,
    ChatMessage,
    Role,
    TextContent,
)

"""
Custom Agent Implementation Example

This sample demonstrates implementing a custom agent by extending BaseAgent class,
showing the minimal requirements for both streaming and non-streaming responses.
"""


class EchoAgent(BaseAgent):
    """A simple custom agent that echoes user messages with a prefix.

    This demonstrates how to create a fully custom agent by extending BaseAgent
    and implementing the required run() and run_stream() methods.
    """

    echo_prefix: str = "Echo: "

    def __init__(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        echo_prefix: str = "Echo: ",
        **kwargs: Any,
    ) -> None:
        """Initialize the EchoAgent.

        Args:
            name: The name of the agent.
            description: The description of the agent.
            echo_prefix: The prefix to add to echoed messages.
            **kwargs: Additional keyword arguments passed to BaseAgent.
        """
        super().__init__(
            name=name,
            description=description,
            echo_prefix=echo_prefix,  # type: ignore
            **kwargs,
        )

    async def run(
        self,
        messages: str | ChatMessage | list[str] | list[ChatMessage] | None = None,
        *,
        thread: AgentThread | None = None,
        **kwargs: Any,
    ) -> AgentRunResponse:
        """Execute the agent and return a complete response.

        Args:
            messages: The message(s) to process.
            thread: The conversation thread (optional).
            **kwargs: Additional keyword arguments.

        Returns:
            An AgentRunResponse containing the agent's reply.
        """
        # Normalize input messages to a list
        normalized_messages = self._normalize_messages(messages)

        if not normalized_messages:
            response_message = ChatMessage(
                role=Role.ASSISTANT,
                contents=[TextContent(text="Hello! I'm a custom echo agent. Send me a message and I'll echo it back.")],
            )
        else:
            # For simplicity, echo the last user message
            last_message = normalized_messages[-1]
            if last_message.text:
                echo_text = f"{self.echo_prefix}{last_message.text}"
            else:
                echo_text = f"{self.echo_prefix}[Non-text message received]"

            response_message = ChatMessage(role=Role.ASSISTANT, contents=[TextContent(text=echo_text)])

        # Notify the thread of new messages if provided
        if thread is not None:
            await self._notify_thread_of_new_messages(thread, normalized_messages, response_message)

        return AgentRunResponse(messages=[response_message])

    async def run_stream(
        self,
        messages: str | ChatMessage | list[str] | list[ChatMessage] | None = None,
        *,
        thread: AgentThread | None = None,
        **kwargs: Any,
    ) -> AsyncIterable[AgentRunResponseUpdate]:
        """Execute the agent and yield streaming response updates.

        Args:
            messages: The message(s) to process.
            thread: The conversation thread (optional).
            **kwargs: Additional keyword arguments.

        Yields:
            AgentRunResponseUpdate objects containing chunks of the response.
        """
        # Normalize input messages to a list
        normalized_messages = self._normalize_messages(messages)

        if not normalized_messages:
            response_text = "Hello! I'm a custom echo agent. Send me a message and I'll echo it back."
        else:
            # For simplicity, echo the last user message
            last_message = normalized_messages[-1]
            if last_message.text:
                response_text = f"{self.echo_prefix}{last_message.text}"
            else:
                response_text = f"{self.echo_prefix}[Non-text message received]"

        # Simulate streaming by yielding the response word by word
        words = response_text.split()
        for i, word in enumerate(words):
            # Add space before word except for the first one
            chunk_text = f" {word}" if i > 0 else word

            yield AgentRunResponseUpdate(
                contents=[TextContent(text=chunk_text)],
                role=Role.ASSISTANT,
            )

            # Small delay to simulate streaming
            await asyncio.sleep(0.1)

        # Notify the thread of the complete response if provided
        if thread is not None:
            complete_response = ChatMessage(role=Role.ASSISTANT, contents=[TextContent(text=response_text)])
            await self._notify_thread_of_new_messages(thread, normalized_messages, complete_response)


async def main() -> None:
    """Demonstrates how to use the custom EchoAgent."""
    print("=== Custom Agent Example ===\n")

    # Create EchoAgent
    print("--- EchoAgent Example ---")
    echo_agent = EchoAgent(
        name="EchoBot", description="A simple agent that echoes messages with a prefix", echo_prefix="🔊 Echo: "
    )

    # Test non-streaming
    print(f"Agent Name: {echo_agent.name}")
    print(f"Agent ID: {echo_agent.id}")
    print(f"Display Name: {echo_agent.display_name}")

    query = "Hello, custom agent!"
    print(f"\nUser: {query}")
    result = await echo_agent.run(query)
    print(f"Agent: {result.messages[0].text}")

    # Test streaming
    query2 = "This is a streaming test"
    print(f"\nUser: {query2}")
    print("Agent: ", end="", flush=True)
    async for chunk in echo_agent.run_stream(query2):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()

    # Example with threads
    print("\n--- Using Custom Agent with Thread ---")
    thread = echo_agent.get_new_thread()

    # First message
    result1 = await echo_agent.run("First message", thread=thread)
    print("User: First message")
    print(f"Agent: {result1.messages[0].text}")

    # Second message in same thread
    result2 = await echo_agent.run("Second message", thread=thread)
    print("User: Second message")
    print(f"Agent: {result2.messages[0].text}")

    # Check conversation history
    if thread.message_store:
        messages = await thread.message_store.list_messages()
        print(f"\nThread contains {len(messages)} messages in history")
    else:
        print("\nThread has no message store configured")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/custom/custom_chat_client.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import random
from collections.abc import AsyncIterable, MutableSequence
from typing import Any, ClassVar

from agent_framework import (
    BaseChatClient,
    ChatMessage,
    ChatOptions,
    ChatResponse,
    ChatResponseUpdate,
    Role,
    TextContent,
    use_chat_middleware,
    use_function_invocation,
)

"""
Custom Chat Client Implementation Example

This sample demonstrates implementing a custom chat client by extending BaseChatClient class,
showing integration with ChatAgent and both streaming and non-streaming responses.
"""


@use_function_invocation
@use_chat_middleware
class EchoingChatClient(BaseChatClient):
    """A custom chat client that echoes messages back with modifications.

    This demonstrates how to implement a custom chat client by extending BaseChatClient
    and implementing the required _inner_get_response() and _inner_get_streaming_response() methods.
    """

    OTEL_PROVIDER_NAME: ClassVar[str] = "EchoingChatClient"

    def __init__(self, *, prefix: str = "Echo:", **kwargs: Any) -> None:
        """Initialize the EchoingChatClient.

        Args:
            prefix: Prefix to add to echoed messages.
            **kwargs: Additional keyword arguments passed to BaseChatClient.
        """
        super().__init__(**kwargs)
        self.prefix = prefix

    async def _inner_get_response(
        self,
        *,
        messages: MutableSequence[ChatMessage],
        chat_options: ChatOptions,
        **kwargs: Any,
    ) -> ChatResponse:
        """Echo back the user's message with a prefix."""
        if not messages:
            response_text = "No messages to echo!"
        else:
            # Echo the last user message
            last_user_message = None
            for message in reversed(messages):
                if message.role == Role.USER:
                    last_user_message = message
                    break

            if last_user_message and last_user_message.text:
                response_text = f"{self.prefix} {last_user_message.text}"
            else:
                response_text = f"{self.prefix} [No text message found]"

        response_message = ChatMessage(role=Role.ASSISTANT, contents=[TextContent(text=response_text)])

        return ChatResponse(
            messages=[response_message],
            model_id="echo-model-v1",
            response_id=f"echo-resp-{random.randint(1000, 9999)}",
        )

    async def _inner_get_streaming_response(
        self,
        *,
        messages: MutableSequence[ChatMessage],
        chat_options: ChatOptions,
        **kwargs: Any,
    ) -> AsyncIterable[ChatResponseUpdate]:
        """Stream back the echoed message character by character."""
        # Get the complete response first
        response = await self._inner_get_response(messages=messages, chat_options=chat_options, **kwargs)

        if response.messages:
            response_text = response.messages[0].text or ""

            # Stream character by character
            for char in response_text:
                yield ChatResponseUpdate(
                    contents=[TextContent(text=char)],
                    role=Role.ASSISTANT,
                    response_id=f"echo-stream-resp-{random.randint(1000, 9999)}",
                    model_id="echo-model-v1",
                )
                await asyncio.sleep(0.05)


async def main() -> None:
    """Demonstrates how to implement and use a custom chat client with ChatAgent."""
    print("=== Custom Chat Client Example ===\n")

    # Create the custom chat client
    print("--- EchoingChatClient Example ---")

    echo_client = EchoingChatClient(prefix="🔊 Echo:")

    # Use the chat client directly
    print("Using chat client directly:")
    direct_response = await echo_client.get_response("Hello, custom chat client!")
    print(f"Direct response: {direct_response.messages[0].text}")

    # Create an agent using the custom chat client
    echo_agent = echo_client.create_agent(
        name="EchoAgent",
        instructions="You are a helpful assistant that echoes back what users say.",
    )

    print(f"\nAgent Name: {echo_agent.name}")
    print(f"Agent Display Name: {echo_agent.display_name}")

    # Test non-streaming with agent
    query = "This is a test message"
    print(f"\nUser: {query}")
    result = await echo_agent.run(query)
    print(f"Agent: {result.messages[0].text}")

    # Test streaming with agent
    query2 = "Stream this message back to me"
    print(f"\nUser: {query2}")
    print("Agent: ", end="", flush=True)
    async for chunk in echo_agent.run_stream(query2):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()

    # Example: Using with threads and conversation history
    print("\n--- Using Custom Chat Client with Thread ---")

    thread = echo_agent.get_new_thread()

    # Multiple messages in conversation
    messages = [
        "Hello, I'm starting a conversation",
        "How are you doing?",
        "Thanks for chatting!",
    ]

    for msg in messages:
        result = await echo_agent.run(msg, thread=thread)
        print(f"User: {msg}")
        print(f"Agent: {result.messages[0].text}\n")

    # Check conversation history
    if thread.message_store:
        thread_messages = await thread.message_store.list_messages()
        print(f"Thread contains {len(thread_messages)} messages")
    else:
        print("Thread has no message store configured")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/ollama/README.md
================================================
# Ollama Examples

This folder contains examples demonstrating how to use Ollama models with the Agent Framework.

## Prerequisites

1. **Install Ollama**: Download and install Ollama from [ollama.com](https://ollama.com/)
2. **Start Ollama**: Ensure Ollama is running on your local machine
3. **Pull a model**: Run `ollama pull mistral` (or any other model you prefer that supports function calling)

## Examples

| File | Description |
|------|-------------|
| [`ollama_with_openai_chat_client.py`](ollama_with_openai_chat_client.py) | Demonstrates how to configure OpenAI Chat Client to use local Ollama models. Shows both streaming and non-streaming responses with tool calling capabilities. |

## Configuration

The examples use environment variables for configuration:

### Environment Variables

Set the following environment variables before running the examples:

- `OLLAMA_ENDPOINT`: The base URL for your Ollama server
  - Example: `export OLLAMA_ENDPOINT="http://localhost:11434/v1/"`

- `OLLAMA_MODEL`: The model name to use
  - Example: `export OLLAMA_MODEL="mistral"`
  - Must be a model you have pulled with Ollama



================================================
FILE: python/samples/getting_started/agents/ollama/ollama_with_openai_chat_client.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIChatClient

"""
Ollama with OpenAI Chat Client Example

This sample demonstrates using Ollama models through OpenAI Chat Client by
configuring the base URL to point to your local Ollama server for local AI inference.
Ollama allows you to run large language models locally on your machine.

Environment Variables:
- OLLAMA_ENDPOINT: The base URL for your Ollama server (e.g., "http://localhost:11434/v1/")
- OLLAMA_MODEL: The model name to use (e.g., "mistral", "llama3.2", "phi3")
"""


def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    agent = OpenAIChatClient(
        api_key="ollama", # Just a placeholder, Ollama doesn't require API key
        base_url=os.getenv("OLLAMA_ENDPOINT"),
        model_id=os.getenv("OLLAMA_MODEL"),
    ).create_agent(
        name="WeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Seattle?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Agent: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    agent = OpenAIChatClient(
        api_key="ollama", # Just a placeholder, Ollama doesn't require API key
        base_url=os.getenv("OLLAMA_ENDPOINT"),
        model_id=os.getenv("OLLAMA_MODEL"),
    ).create_agent(
        name="WeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Portland?"
    print(f"User: {query}")
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run_stream(query):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


async def main() -> None:
    print("=== Ollama with OpenAI Chat Client Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/README.md
================================================
# OpenAI Agent Framework Examples

This folder contains examples demonstrating different ways to create and use agents with the OpenAI Assistants client from the `agent_framework.openai` package.

## Examples

| File | Description |
|------|-------------|
| [`openai_assistants_basic.py`](openai_assistants_basic.py) | The simplest way to create an agent using `ChatAgent` with `OpenAIAssistantsClient`. Shows both streaming and non-streaming responses with automatic assistant creation and cleanup. |
| [`openai_assistants_with_existing_assistant.py`](openai_assistants_with_existing_assistant.py) | Shows how to work with a pre-existing assistant by providing the assistant ID to the OpenAI Assistants client. Demonstrates proper cleanup of manually created assistants. |
| [`openai_assistants_with_explicit_settings.py`](openai_assistants_with_explicit_settings.py) | Shows how to initialize an agent with a specific assistants client, configuring settings explicitly including API key and model ID. |
| [`openai_assistants_with_function_tools.py`](openai_assistants_with_function_tools.py) | Demonstrates how to use function tools with agents. Shows both agent-level tools (defined when creating the agent) and query-level tools (provided with specific queries). |
| [`openai_assistants_with_code_interpreter.py`](openai_assistants_with_code_interpreter.py) | Shows how to use the HostedCodeInterpreterTool with OpenAI agents to write and execute Python code. Includes helper methods for accessing code interpreter data from response chunks. |
| [`openai_assistants_with_file_search.py`](openai_assistants_with_file_search.py) | Demonstrates how to use file search capabilities with OpenAI agents, allowing the agent to search through uploaded files to answer questions. |
| [`openai_assistants_with_thread.py`](openai_assistants_with_thread.py) | Demonstrates thread management with OpenAI agents, including automatic thread creation for stateless conversations and explicit thread management for maintaining conversation context across multiple interactions. |
| [`openai_chat_client_basic.py`](openai_chat_client_basic.py) | The simplest way to create an agent using `ChatAgent` with `OpenAIChatClient`. Shows both streaming and non-streaming responses for chat-based interactions with OpenAI models. |
| [`openai_chat_client_with_explicit_settings.py`](openai_chat_client_with_explicit_settings.py) | Shows how to initialize an agent with a specific chat client, configuring settings explicitly including API key and model ID. |
| [`openai_chat_client_with_function_tools.py`](openai_chat_client_with_function_tools.py) | Demonstrates how to use function tools with agents. Shows both agent-level tools (defined when creating the agent) and query-level tools (provided with specific queries). |
| [`openai_chat_client_with_local_mcp.py`](openai_chat_client_with_local_mcp.py) | Shows how to integrate OpenAI agents with local Model Context Protocol (MCP) servers for enhanced functionality and tool integration. |
| [`openai_chat_client_with_thread.py`](openai_chat_client_with_thread.py) | Demonstrates thread management with OpenAI agents, including automatic thread creation for stateless conversations and explicit thread management for maintaining conversation context across multiple interactions. |
| [`openai_chat_client_with_web_search.py`](openai_chat_client_with_web_search.py) | Shows how to use web search capabilities with OpenAI agents to retrieve and use information from the internet in responses. |
| [`openai_responses_client_basic.py`](openai_responses_client_basic.py) | The simplest way to create an agent using `ChatAgent` with `OpenAIResponsesClient`. Shows both streaming and non-streaming responses for structured response generation with OpenAI models. |
| [`openai_responses_client_image_analysis.py`](openai_responses_client_image_analysis.py) | Demonstrates how to use vision capabilities with agents to analyze images. |
| [`openai_responses_client_reasoning.py`](openai_responses_client_reasoning.py) | Demonstrates how to use reasoning capabilities with OpenAI agents, showing how the agent can provide detailed reasoning for its responses. |
| [`openai_responses_client_with_code_interpreter.py`](openai_responses_client_with_code_interpreter.py) | Shows how to use the HostedCodeInterpreterTool with OpenAI agents to write and execute Python code. Includes helper methods for accessing code interpreter data from response chunks. |
| [`openai_responses_client_with_explicit_settings.py`](openai_responses_client_with_explicit_settings.py) | Shows how to initialize an agent with a specific responses client, configuring settings explicitly including API key and model ID. |
| [`openai_responses_client_with_file_search.py`](openai_responses_client_with_file_search.py) | Demonstrates how to use file search capabilities with OpenAI agents, allowing the agent to search through uploaded files to answer questions. |
| [`openai_responses_client_with_function_tools.py`](openai_responses_client_with_function_tools.py) | Demonstrates how to use function tools with agents. Shows both agent-level tools (defined when creating the agent) and run-level tools (provided with specific queries). |
| [`openai_responses_client_with_hosted_mcp.py`](openai_responses_client_with_hosted_mcp.py) | Shows how to integrate OpenAI agents with hosted Model Context Protocol (MCP) servers, including approval workflows and tool management for remote MCP services. |
| [`openai_responses_client_with_local_mcp.py`](openai_responses_client_with_local_mcp.py) | Shows how to integrate OpenAI agents with local Model Context Protocol (MCP) servers for enhanced functionality and tool integration. |
| [`openai_responses_client_with_structured_output.py`](openai_responses_client_with_structured_output.py) | Demonstrates how to use structured outputs with OpenAI agents to get structured data responses in predefined formats. |
| [`openai_responses_client_with_thread.py`](openai_responses_client_with_thread.py) | Demonstrates thread management with OpenAI agents, including automatic thread creation for stateless conversations and explicit thread management for maintaining conversation context across multiple interactions. |
| [`openai_responses_client_with_web_search.py`](openai_responses_client_with_web_search.py) | Shows how to use web search capabilities with OpenAI agents to retrieve and use information from the internet in responses. |

## Environment Variables

Make sure to set the following environment variables before running the examples:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_CHAT_MODEL_ID`: The OpenAI model to use (e.g., `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`)
- `OPENAI_RESPONSES_MODEL_ID`: The OpenAI model to use (e.g., `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`)
- For image processing examples, use a vision-capable model like `gpt-4o` or `gpt-4o-mini`

Optionally, you can set:
- `OPENAI_ORG_ID`: Your OpenAI organization ID (if applicable)
- `OPENAI_API_BASE_URL`: Your OpenAI base URL (if using a different base URL)

## Optional Dependencies

Some examples require additional dependencies:

- **Image Generation Example**: The `openai_responses_client_image_generation.py` example requires PIL (Pillow) for image display. Install with:
  ```bash
  # Using uv
  uv add pillow

  # Or using pip
  pip install pillow
  ```



================================================
FILE: python/samples/getting_started/agents/openai/openai_assistants_basic.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIAssistantsClient
from pydantic import Field

"""
OpenAI Assistants Basic Example

This sample demonstrates basic usage of OpenAIAssistantsClient with automatic
assistant lifecycle management, showing both streaming and non-streaming responses.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    # Since no assistant ID is provided, the assistant will be automatically created
    # and deleted after getting a response
    async with OpenAIAssistantsClient().create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        query = "What's the weather like in Seattle?"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    # Since no assistant ID is provided, the assistant will be automatically created
    # and deleted after getting a response
    async with OpenAIAssistantsClient().create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        query = "What's the weather like in Portland?"
        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream(query):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")


async def main() -> None:
    print("=== Basic OpenAI Assistants Chat Client Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_assistants_with_code_interpreter.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import AgentRunResponseUpdate, ChatAgent, ChatResponseUpdate, HostedCodeInterpreterTool
from agent_framework.openai import OpenAIAssistantsClient
from openai.types.beta.threads.runs import (
    CodeInterpreterToolCallDelta,
    RunStepDelta,
    RunStepDeltaEvent,
    ToolCallDeltaObject,
)
from openai.types.beta.threads.runs.code_interpreter_tool_call_delta import CodeInterpreter

"""
OpenAI Assistants with Code Interpreter Example

This sample demonstrates using HostedCodeInterpreterTool with OpenAI Assistants
for Python code execution and mathematical problem solving.
"""


def get_code_interpreter_chunk(chunk: AgentRunResponseUpdate) -> str | None:
    """Helper method to access code interpreter data."""
    if (
        isinstance(chunk.raw_representation, ChatResponseUpdate)
        and isinstance(chunk.raw_representation.raw_representation, RunStepDeltaEvent)
        and isinstance(chunk.raw_representation.raw_representation.delta, RunStepDelta)
        and isinstance(chunk.raw_representation.raw_representation.delta.step_details, ToolCallDeltaObject)
        and chunk.raw_representation.raw_representation.delta.step_details.tool_calls
    ):
        for tool_call in chunk.raw_representation.raw_representation.delta.step_details.tool_calls:
            if (
                isinstance(tool_call, CodeInterpreterToolCallDelta)
                and isinstance(tool_call.code_interpreter, CodeInterpreter)
                and tool_call.code_interpreter.input is not None
            ):
                return tool_call.code_interpreter.input
    return None


async def main() -> None:
    """Example showing how to use the HostedCodeInterpreterTool with OpenAI Assistants."""
    print("=== OpenAI Assistants Agent with Code Interpreter Example ===")

    async with ChatAgent(
        chat_client=OpenAIAssistantsClient(),
        instructions="You are a helpful assistant that can write and execute Python code to solve problems.",
        tools=HostedCodeInterpreterTool(),
    ) as agent:
        query = "Use code to get the factorial of 100?"
        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        generated_code = ""
        async for chunk in agent.run_stream(query):
            if chunk.text:
                print(chunk.text, end="", flush=True)
            code_interpreter_chunk = get_code_interpreter_chunk(chunk)
            if code_interpreter_chunk is not None:
                generated_code += code_interpreter_chunk

        print(f"\nGenerated code:\n{generated_code}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_assistants_with_existing_assistant.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIAssistantsClient
from openai import AsyncOpenAI
from pydantic import Field

"""
OpenAI Assistants with Existing Assistant Example

This sample demonstrates working with pre-existing OpenAI Assistants
using existing assistant IDs rather than creating new ones.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    print("=== OpenAI Assistants Chat Client with Existing Assistant ===")

    # Create the client
    client = AsyncOpenAI()

    # Create an assistant that will persist
    created_assistant = await client.beta.assistants.create(
        model=os.environ["OPENAI_CHAT_MODEL_ID"], name="WeatherAssistant"
    )

    try:
        async with ChatAgent(
            chat_client=OpenAIAssistantsClient(async_client=client, assistant_id=created_assistant.id),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent:
            result = await agent.run("What's the weather like in Tokyo?")
            print(f"Result: {result}\n")
    finally:
        # Clean up the assistant manually
        await client.beta.assistants.delete(created_assistant.id)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_assistants_with_explicit_settings.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIAssistantsClient
from pydantic import Field

"""
OpenAI Assistants with Explicit Settings Example

This sample demonstrates creating OpenAI Assistants with explicit configuration
settings rather than relying on environment variable defaults.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    print("=== OpenAI Assistants Client with Explicit Settings ===")

    async with OpenAIAssistantsClient(
        model_id=os.environ["OPENAI_CHAT_MODEL_ID"],
        api_key=os.environ["OPENAI_API_KEY"],
    ).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        result = await agent.run("What's the weather like in New York?")
        print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_assistants_with_file_search.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import ChatAgent, HostedFileSearchTool, HostedVectorStoreContent
from agent_framework.openai import OpenAIAssistantsClient

"""
OpenAI Assistants with File Search Example

This sample demonstrates using HostedFileSearchTool with OpenAI Assistants
for document-based question answering and information retrieval.
"""

# Helper functions


async def create_vector_store(client: OpenAIAssistantsClient) -> tuple[str, HostedVectorStoreContent]:
    """Create a vector store with sample documents."""
    file = await client.client.files.create(
        file=("todays_weather.txt", b"The weather today is sunny with a high of 75F."), purpose="user_data"
    )
    vector_store = await client.client.vector_stores.create(
        name="knowledge_base",
        expires_after={"anchor": "last_active_at", "days": 1},
    )
    result = await client.client.vector_stores.files.create_and_poll(vector_store_id=vector_store.id, file_id=file.id)
    if result.last_error is not None:
        raise Exception(f"Vector store file processing failed with status: {result.last_error.message}")

    return file.id, HostedVectorStoreContent(vector_store_id=vector_store.id)


async def delete_vector_store(client: OpenAIAssistantsClient, file_id: str, vector_store_id: str) -> None:
    """Delete the vector store after using it."""

    await client.client.vector_stores.delete(vector_store_id=vector_store_id)
    await client.client.files.delete(file_id=file_id)


async def main() -> None:
    print("=== OpenAI Assistants Client Agent with File Search Example ===\n")

    client = OpenAIAssistantsClient()
    async with ChatAgent(
        chat_client=client,
        instructions="You are a helpful assistant that searches files in a knowledge base.",
        tools=HostedFileSearchTool(),
    ) as agent:
        query = "What is the weather today? Do a file search to find the answer."
        file_id, vector_store = await create_vector_store(client)

        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream(
            query, tool_resources={"file_search": {"vector_store_ids": [vector_store.vector_store_id]}}
        ):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        await delete_vector_store(client, file_id, vector_store.vector_store_id)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_assistants_with_function_tools.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from datetime import datetime, timezone
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIAssistantsClient
from pydantic import Field

"""
OpenAI Assistants with Function Tools Example

This sample demonstrates function tool integration with OpenAI Assistants,
showing both agent-level and query-level tool configuration patterns.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    async with ChatAgent(
        chat_client=OpenAIAssistantsClient(),
        instructions="You are a helpful assistant that can provide weather and time information.",
        tools=[get_weather, get_time],  # Tools defined at agent creation
    ) as agent:
        # First query - agent can use weather tool
        query1 = "What's the weather like in New York?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"Agent: {result1}\n")

        # Second query - agent can use time tool
        query2 = "What's the current UTC time?"
        print(f"User: {query2}")
        result2 = await agent.run(query2)
        print(f"Agent: {result2}\n")

        # Third query - agent can use both tools if needed
        query3 = "What's the weather in London and what's the current UTC time?"
        print(f"User: {query3}")
        result3 = await agent.run(query3)
        print(f"Agent: {result3}\n")


async def tools_on_run_level() -> None:
    """Example showing tools passed to the run method."""
    print("=== Tools Passed to Run Method ===")

    # Agent created without tools
    async with ChatAgent(
        chat_client=OpenAIAssistantsClient(),
        instructions="You are a helpful assistant.",
        # No tools defined here
    ) as agent:
        # First query with weather tool
        query1 = "What's the weather like in Seattle?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, tools=[get_weather])  # Tool passed to run method
        print(f"Agent: {result1}\n")

        # Second query with time tool
        query2 = "What's the current UTC time?"
        print(f"User: {query2}")
        result2 = await agent.run(query2, tools=[get_time])  # Different tool for this query
        print(f"Agent: {result2}\n")

        # Third query with multiple tools
        query3 = "What's the weather in Chicago and what's the current UTC time?"
        print(f"User: {query3}")
        result3 = await agent.run(query3, tools=[get_weather, get_time])  # Multiple tools
        print(f"Agent: {result3}\n")


async def mixed_tools_example() -> None:
    """Example showing both agent-level tools and run-method tools."""
    print("=== Mixed Tools Example (Agent + Run Method) ===")

    # Agent created with some base tools
    async with ChatAgent(
        chat_client=OpenAIAssistantsClient(),
        instructions="You are a comprehensive assistant that can help with various information requests.",
        tools=[get_weather],  # Base tool available for all queries
    ) as agent:
        # Query using both agent tool and additional run-method tools
        query = "What's the weather in Denver and what's the current UTC time?"
        print(f"User: {query}")

        # Agent has access to get_weather (from creation) + additional tools from run method
        result = await agent.run(
            query,
            tools=[get_time],  # Additional tools for this specific query
        )
        print(f"Agent: {result}\n")


async def main() -> None:
    print("=== OpenAI Assistants Chat Client Agent with Function Tools Examples ===\n")

    await tools_on_agent_level()
    await tools_on_run_level()
    await mixed_tools_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_assistants_with_thread.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework import AgentThread, ChatAgent
from agent_framework.openai import OpenAIAssistantsClient
from pydantic import Field

"""
OpenAI Assistants with Thread Management Example

This sample demonstrates thread management with OpenAI Assistants, showing
persistent conversation threads and context preservation across interactions.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def example_with_automatic_thread_creation() -> None:
    """Example showing automatic thread creation (service-managed thread)."""
    print("=== Automatic Thread Creation Example ===")

    async with ChatAgent(
        chat_client=OpenAIAssistantsClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        # First conversation - no thread provided, will be created automatically
        query1 = "What's the weather like in Seattle?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"Agent: {result1.text}")

        # Second conversation - still no thread provided, will create another new thread
        query2 = "What was the last city I asked about?"
        print(f"\nUser: {query2}")
        result2 = await agent.run(query2)
        print(f"Agent: {result2.text}")
        print("Note: Each call creates a separate thread, so the agent doesn't remember previous context.\n")


async def example_with_thread_persistence() -> None:
    """Example showing thread persistence across multiple conversations."""
    print("=== Thread Persistence Example ===")
    print("Using the same thread across multiple conversations to maintain context.\n")

    async with ChatAgent(
        chat_client=OpenAIAssistantsClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        # Create a new thread that will be reused
        thread = agent.get_new_thread()

        # First conversation
        query1 = "What's the weather like in Tokyo?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, thread=thread)
        print(f"Agent: {result1.text}")

        # Second conversation using the same thread - maintains context
        query2 = "How about London?"
        print(f"\nUser: {query2}")
        result2 = await agent.run(query2, thread=thread)
        print(f"Agent: {result2.text}")

        # Third conversation - agent should remember both previous cities
        query3 = "Which of the cities I asked about has better weather?"
        print(f"\nUser: {query3}")
        result3 = await agent.run(query3, thread=thread)
        print(f"Agent: {result3.text}")
        print("Note: The agent remembers context from previous messages in the same thread.\n")


async def example_with_existing_thread_id() -> None:
    """Example showing how to work with an existing thread ID from the service."""
    print("=== Existing Thread ID Example ===")
    print("Using a specific thread ID to continue an existing conversation.\n")

    # First, create a conversation and capture the thread ID
    existing_thread_id = None

    async with ChatAgent(
        chat_client=OpenAIAssistantsClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    ) as agent:
        # Start a conversation and get the thread ID
        thread = agent.get_new_thread()
        query1 = "What's the weather in Paris?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, thread=thread)
        print(f"Agent: {result1.text}")

        # The thread ID is set after the first response
        existing_thread_id = thread.service_thread_id
        print(f"Thread ID: {existing_thread_id}")

    if existing_thread_id:
        print("\n--- Continuing with the same thread ID in a new agent instance ---")

        # Create a new agent instance but use the existing thread ID
        async with ChatAgent(
            chat_client=OpenAIAssistantsClient(thread_id=existing_thread_id),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        ) as agent:
            # Create a thread with the existing ID
            thread = AgentThread(service_thread_id=existing_thread_id)

            query2 = "What was the last city I asked about?"
            print(f"User: {query2}")
            result2 = await agent.run(query2, thread=thread)
            print(f"Agent: {result2.text}")
            print("Note: The agent continues the conversation from the previous thread.\n")


async def main() -> None:
    print("=== OpenAI Assistants Chat Client Agent Thread Management Examples ===\n")

    await example_with_automatic_thread_creation()
    await example_with_thread_persistence()
    await example_with_existing_thread_id()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_chat_client_basic.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIChatClient

"""
OpenAI Chat Client Basic Example

This sample demonstrates basic usage of OpenAIChatClient for direct chat-based
interactions, showing both streaming and non-streaming responses.
"""


def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    agent = OpenAIChatClient().create_agent(
        name="WeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Seattle?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Result: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    agent = OpenAIChatClient().create_agent(
        name="WeatherAgent",
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Portland?"
    print(f"User: {query}")
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run_stream(query):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


async def main() -> None:
    print("=== Basic OpenAI Chat Client Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_chat_client_with_explicit_settings.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIChatClient
from pydantic import Field

"""
OpenAI Chat Client with Explicit Settings Example

This sample demonstrates creating OpenAI Chat Client with explicit configuration
settings rather than relying on environment variable defaults.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    print("=== OpenAI Chat Client with Explicit Settings ===")

    agent = OpenAIChatClient(
        model_id=os.environ["OPENAI_CHAT_MODEL_ID"],
        api_key=os.environ["OPENAI_API_KEY"],
    ).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    result = await agent.run("What's the weather like in New York?")
    print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_chat_client_with_function_tools.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from datetime import datetime, timezone
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from pydantic import Field

"""
OpenAI Chat Client with Function Tools Example

This sample demonstrates function tool integration with OpenAI Chat Client,
showing both agent-level and query-level tool configuration patterns.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    agent = ChatAgent(
        chat_client=OpenAIChatClient(),
        instructions="You are a helpful assistant that can provide weather and time information.",
        tools=[get_weather, get_time],  # Tools defined at agent creation
    )

    # First query - agent can use weather tool
    query1 = "What's the weather like in New York?"
    print(f"User: {query1}")
    result1 = await agent.run(query1)
    print(f"Agent: {result1}\n")

    # Second query - agent can use time tool
    query2 = "What's the current UTC time?"
    print(f"User: {query2}")
    result2 = await agent.run(query2)
    print(f"Agent: {result2}\n")

    # Third query - agent can use both tools if needed
    query3 = "What's the weather in London and what's the current UTC time?"
    print(f"User: {query3}")
    result3 = await agent.run(query3)
    print(f"Agent: {result3}\n")


async def tools_on_run_level() -> None:
    """Example showing tools passed to the run method."""
    print("=== Tools Passed to Run Method ===")

    # Agent created without tools
    agent = ChatAgent(
        chat_client=OpenAIChatClient(),
        instructions="You are a helpful assistant.",
        # No tools defined here
    )

    # First query with weather tool
    query1 = "What's the weather like in Seattle?"
    print(f"User: {query1}")
    result1 = await agent.run(query1, tools=[get_weather])  # Tool passed to run method
    print(f"Agent: {result1}\n")

    # Second query with time tool
    query2 = "What's the current UTC time?"
    print(f"User: {query2}")
    result2 = await agent.run(query2, tools=[get_time])  # Different tool for this query
    print(f"Agent: {result2}\n")

    # Third query with multiple tools
    query3 = "What's the weather in Chicago and what's the current UTC time?"
    print(f"User: {query3}")
    result3 = await agent.run(query3, tools=[get_weather, get_time])  # Multiple tools
    print(f"Agent: {result3}\n")


async def mixed_tools_example() -> None:
    """Example showing both agent-level tools and run-method tools."""
    print("=== Mixed Tools Example (Agent + Run Method) ===")

    # Agent created with some base tools
    agent = ChatAgent(
        chat_client=OpenAIChatClient(),
        instructions="You are a comprehensive assistant that can help with various information requests.",
        tools=[get_weather],  # Base tool available for all queries
    )

    # Query using both agent tool and additional run-method tools
    query = "What's the weather in Denver and what's the current UTC time?"
    print(f"User: {query}")

    # Agent has access to get_weather (from creation) + additional tools from run method
    result = await agent.run(
        query,
        tools=[get_time],  # Additional tools for this specific query
    )
    print(f"Agent: {result}\n")


async def main() -> None:
    print("=== OpenAI Chat Client Agent with Function Tools Examples ===\n")

    await tools_on_agent_level()
    await tools_on_run_level()
    await mixed_tools_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_chat_client_with_local_mcp.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.openai import OpenAIChatClient

"""
OpenAI Chat Client with Local MCP Example

This sample demonstrates integrating Model Context Protocol (MCP) tools with
OpenAI Chat Client for extended functionality and external service access.
"""


async def mcp_tools_on_run_level() -> None:
    """Example showing MCP tools defined when running the agent."""
    print("=== Tools Defined on Run Level ===")

    # Tools are provided when running the agent
    # This means we have to ensure we connect to the MCP server before running the agent
    # and pass the tools to the run method.
    async with (
        MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
        ) as mcp_server,
        ChatAgent(
            chat_client=OpenAIChatClient(),
            name="DocsAgent",
            instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        ) as agent,
    ):
        # First query
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        result1 = await agent.run(query1, tools=mcp_server)
        print(f"{agent.name}: {result1}\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        result2 = await agent.run(query2, tools=mcp_server)
        print(f"{agent.name}: {result2}\n")


async def mcp_tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    # The agent will connect to the MCP server through its context manager.
    async with OpenAIChatClient().create_agent(
        name="DocsAgent",
        instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        tools=MCPStreamableHTTPTool(  # Tools defined at agent creation
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
        ),
    ) as agent:
        # First query
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"{agent.name}: {result1}\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        result2 = await agent.run(query2)
        print(f"{agent.name}: {result2}\n")


async def main() -> None:
    print("=== OpenAI Chat Client Agent with MCP Tools Examples ===\n")

    await mcp_tools_on_agent_level()
    await mcp_tools_on_run_level()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_chat_client_with_thread.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework import AgentThread, ChatAgent, ChatMessageStore
from agent_framework.openai import OpenAIChatClient
from pydantic import Field

"""
OpenAI Chat Client with Thread Management Example

This sample demonstrates thread management with OpenAI Chat Client, showing
conversation threads and message history preservation across interactions.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def example_with_automatic_thread_creation() -> None:
    """Example showing automatic thread creation (service-managed thread)."""
    print("=== Automatic Thread Creation Example ===")

    agent = ChatAgent(
        chat_client=OpenAIChatClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # First conversation - no thread provided, will be created automatically
    query1 = "What's the weather like in Seattle?"
    print(f"User: {query1}")
    result1 = await agent.run(query1)
    print(f"Agent: {result1.text}")

    # Second conversation - still no thread provided, will create another new thread
    query2 = "What was the last city I asked about?"
    print(f"\nUser: {query2}")
    result2 = await agent.run(query2)
    print(f"Agent: {result2.text}")
    print("Note: Each call creates a separate thread, so the agent doesn't remember previous context.\n")


async def example_with_thread_persistence() -> None:
    """Example showing thread persistence across multiple conversations."""
    print("=== Thread Persistence Example ===")
    print("Using the same thread across multiple conversations to maintain context.\n")

    agent = ChatAgent(
        chat_client=OpenAIChatClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # Create a new thread that will be reused
    thread = agent.get_new_thread()

    # First conversation
    query1 = "What's the weather like in Tokyo?"
    print(f"User: {query1}")
    result1 = await agent.run(query1, thread=thread)
    print(f"Agent: {result1.text}")

    # Second conversation using the same thread - maintains context
    query2 = "How about London?"
    print(f"\nUser: {query2}")
    result2 = await agent.run(query2, thread=thread)
    print(f"Agent: {result2.text}")

    # Third conversation - agent should remember both previous cities
    query3 = "Which of the cities I asked about has better weather?"
    print(f"\nUser: {query3}")
    result3 = await agent.run(query3, thread=thread)
    print(f"Agent: {result3.text}")
    print("Note: The agent remembers context from previous messages in the same thread.\n")


async def example_with_existing_thread_messages() -> None:
    """Example showing how to work with existing thread messages for OpenAI."""
    print("=== Existing Thread Messages Example ===")

    agent = ChatAgent(
        chat_client=OpenAIChatClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # Start a conversation and build up message history
    thread = agent.get_new_thread()

    query1 = "What's the weather in Paris?"
    print(f"User: {query1}")
    result1 = await agent.run(query1, thread=thread)
    print(f"Agent: {result1.text}")

    # The thread now contains the conversation history in memory
    if thread.message_store:
        messages = await thread.message_store.list_messages()
        print(f"Thread contains {len(messages or [])} messages")

    print("\n--- Continuing with the same thread in a new agent instance ---")

    # Create a new agent instance but use the existing thread with its message history
    new_agent = ChatAgent(
        chat_client=OpenAIChatClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # Use the same thread object which contains the conversation history
    query2 = "What was the last city I asked about?"
    print(f"User: {query2}")
    result2 = await new_agent.run(query2, thread=thread)
    print(f"Agent: {result2.text}")
    print("Note: The agent continues the conversation using the local message history.\n")

    print("\n--- Alternative: Creating a new thread from existing messages ---")

    # You can also create a new thread from existing messages
    messages = await thread.message_store.list_messages() if thread.message_store else []

    new_thread = AgentThread(message_store=ChatMessageStore(messages))

    query3 = "How does the Paris weather compare to London?"
    print(f"User: {query3}")
    result3 = await new_agent.run(query3, thread=new_thread)
    print(f"Agent: {result3.text}")
    print("Note: This creates a new thread with the same conversation history.\n")


async def main() -> None:
    print("=== OpenAI Chat Client Agent Thread Management Examples ===\n")

    await example_with_automatic_thread_creation()
    await example_with_thread_persistence()
    await example_with_existing_thread_messages()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_chat_client_with_web_search.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import HostedWebSearchTool
from agent_framework.openai import OpenAIChatClient

"""
OpenAI Chat Client with Web Search Example

This sample demonstrates using HostedWebSearchTool with OpenAI Chat Client
for real-time information retrieval and current data access.
"""


async def main() -> None:
    client = OpenAIChatClient(model_id="gpt-4o-search-preview")

    message = "What is the current weather? Do not ask for my current location."
    # Test that the client will use the web search tool with location
    additional_properties = {
        "user_location": {
            "country": "US",
            "city": "Seattle",
        }
    }
    stream = False
    print(f"User: {message}")
    if stream:
        print("Assistant: ", end="")
        async for chunk in client.get_streaming_response(
            message,
            tools=[HostedWebSearchTool(additional_properties=additional_properties)],
            tool_choice="auto",
        ):
            if chunk.text:
                print(chunk.text, end="")
        print("")
    else:
        response = await client.get_response(
            message,
            tools=[HostedWebSearchTool(additional_properties=additional_properties)],
            tool_choice="auto",
        )
        print(f"Assistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_basic.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient
from pydantic import Field

"""
OpenAI Responses Client Basic Example

This sample demonstrates basic usage of OpenAIResponsesClient for structured
response generation, showing both streaming and non-streaming responses.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def non_streaming_example() -> None:
    """Example of non-streaming response (get the complete result at once)."""
    print("=== Non-streaming Response Example ===")

    agent = ChatAgent(
        chat_client=OpenAIResponsesClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Seattle?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Result: {result}\n")


async def streaming_example() -> None:
    """Example of streaming response (get results as they are generated)."""
    print("=== Streaming Response Example ===")

    agent = ChatAgent(
        chat_client=OpenAIResponsesClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    query = "What's the weather like in Portland?"
    print(f"User: {query}")
    print("Agent: ", end="", flush=True)
    async for chunk in agent.run_stream(query):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")


async def main() -> None:
    print("=== Basic OpenAI Responses Client Agent Example ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_image_analysis.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import ChatMessage, TextContent, UriContent
from agent_framework.openai import OpenAIResponsesClient

"""
OpenAI Responses Client Image Analysis Example

This sample demonstrates using OpenAI Responses Client for image analysis and vision tasks,
showing multi-modal content handling with text and images.
"""


async def main():
    print("=== OpenAI Responses Agent with Image Analysis ===")

    # 1. Create an OpenAI Responses agent with vision capabilities
    agent = OpenAIResponsesClient().create_agent(
        name="VisionAgent",
        instructions="You are a helpful agent that can analyze images.",
    )

    # 2. Create a simple message with both text and image content
    user_message = ChatMessage(
        role="user",
        contents=[
            TextContent(text="What do you see in this image?"),
            UriContent(
                uri="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                media_type="image/jpeg",
            ),
        ],
    )

    # 3. Get the agent's response
    print("User: What do you see in this image? [Image provided]")
    result = await agent.run(user_message)
    print(f"Agent: {result.text}")
    print()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_image_generation.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import base64

from agent_framework import DataContent, UriContent
from agent_framework.openai import OpenAIResponsesClient

"""
OpenAI Responses Client Image Generation Example

This sample demonstrates how to generate images using OpenAI's DALL-E models
through the Responses Client. Image generation capabilities enable AI to create visual content from text,
making it ideal for creative applications, content creation, design prototyping,
and automated visual asset generation.
"""


def show_image_info(data_uri: str) -> None:
    """Display information about the generated image."""
    try:
        # Extract format and size info from data URI
        if data_uri.startswith("data:image/"):
            format_info = data_uri.split(";")[0].split("/")[1]
            base64_data = data_uri.split(",", 1)[1]
            image_bytes = base64.b64decode(base64_data)
            size_kb = len(image_bytes) / 1024

            print(" Image successfully generated!")
            print(f"   Format: {format_info.upper()}")
            print(f"   Size: {size_kb:.1f} KB")
            print(f"   Data URI length: {len(data_uri)} characters")
            print("")
            print(" To save and view the image:")
            print('   1. Install Pillow: "pip install pillow" or "uv add pillow"')
            print("   2. Use the data URI in your code to save/display the image")
            print("   3. Or copy the base64 data to an online base64 image decoder")
        else:
            print(f" Image URL generated: {data_uri}")
            print(" You can open this URL in a browser to view the image")

    except Exception as e:
        print(f" Error processing image data: {e}")
        print(" Image generated but couldn't parse details")


async def main() -> None:
    print("=== OpenAI Responses Image Generation Agent Example ===")

    # Create an agent with customized image generation options
    agent = OpenAIResponsesClient().create_agent(
        instructions="You are a helpful AI that can generate images.",
        tools=[
            {
                "type": "image_generation",
                # Core parameters
                "size": "1024x1024",
                "background": "transparent",
                "quality": "low",
                "format": "webp",
            }
        ],
    )

    query = "Generate a nice beach scenery with blue skies in summer time."
    print(f"User: {query}")
    print("Generating image with parameters: 1024x1024 size, transparent background, low quality, WebP format...")

    result = await agent.run(query)
    print(f"Agent: {result.text}")

    # Show information about the generated image
    for message in result.messages:
        for content in message.contents:
            if isinstance(content, (DataContent, UriContent)) and content.uri:
                show_image_info(content.uri)
                break


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_reasoning.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework.openai import OpenAIResponsesClient

"""
OpenAI Responses Client Reasoning Example

This sample demonstrates advanced reasoning capabilities using OpenAI's gpt-5 models,
showing step-by-step reasoning process visualization and complex problem-solving.

This uses the additional_chat_options parameter to enable reasoning with high effort and detailed summaries.
You can also set these options at the run level, since they are api and/or provider specific, you will need to lookup
the correct values for your provider, since these are passed through as-is.

In this case they are here: https://platform.openai.com/docs/api-reference/responses/create#responses-create-reasoning
"""


agent = OpenAIResponsesClient(model_id="gpt-5").create_agent(
    name="MathHelper",
    instructions="You are a personal math tutor. When asked a math question, "
    "reason over how best to approach the problem and share your thought process.",
    additional_chat_options={"reasoning": {"effort": "high", "summary": "detailed"}},
)


async def reasoning_example() -> None:
    """Example of reasoning response (get results as they are generated)."""
    print("\033[92m=== Reasoning Example ===\033[0m")

    query = "I need to solve the equation 3x + 11 = 14 and I need to prove the pythagorean theorem. Can you help me?"
    print(f"User: {query}")
    print(f"{agent.name}: ", end="", flush=True)
    response = await agent.run(query)
    for msg in response.messages:
        if msg.contents:
            for content in msg.contents:
                if content.type == "text_reasoning":
                    print(f"\033[94m{content.text}\033[0m", end="", flush=True)
                elif content.type == "text":
                    print(content.text, end="", flush=True)
    print("\n")
    if response.usage_details:
        print(f"Usage: {response.usage_details}")


async def streaming_reasoning_example() -> None:
    """Example of reasoning response (get results as they are generated)."""
    print("\033[92m=== Streaming Reasoning Example ===\033[0m")

    query = "I need to solve the equation 3x + 11 = 14 and I need to prove the pythagorean theorem. Can you help me?"
    print(f"User: {query}")
    print(f"{agent.name}: ", end="", flush=True)
    usage = None
    async for chunk in agent.run_stream(query):
        if chunk.contents:
            for content in chunk.contents:
                if content.type == "text_reasoning":
                    print(f"\033[94m{content.text}\033[0m", end="", flush=True)
                elif content.type == "text":
                    print(content.text, end="", flush=True)
                elif content.type == "usage":
                    usage = content
    print("\n")
    if usage:
        print(f"Usage: {usage.details}")


async def main() -> None:
    print("\033[92m=== Basic OpenAI Responses Reasoning Agent Example ===\033[0m")

    await reasoning_example()
    await streaming_reasoning_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_with_code_interpreter.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import ChatAgent, ChatResponse, HostedCodeInterpreterTool
from agent_framework.openai import OpenAIResponsesClient
from openai.types.responses.response import Response as OpenAIResponse
from openai.types.responses.response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall

"""
OpenAI Responses Client with Code Interpreter Example

This sample demonstrates using HostedCodeInterpreterTool with OpenAI Responses Client
for Python code execution and mathematical problem solving.
"""


async def main() -> None:
    """Example showing how to use the HostedCodeInterpreterTool with OpenAI Responses."""
    print("=== OpenAI Responses Agent with Code Interpreter Example ===")

    agent = ChatAgent(
        chat_client=OpenAIResponsesClient(),
        instructions="You are a helpful assistant that can write and execute Python code to solve problems.",
        tools=HostedCodeInterpreterTool(),
    )

    query = "Use code to get the factorial of 100?"
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Result: {result}\n")

    if (
        isinstance(result.raw_representation, ChatResponse)
        and isinstance(result.raw_representation.raw_representation, OpenAIResponse)
        and len(result.raw_representation.raw_representation.output) > 0
        and isinstance(result.raw_representation.raw_representation.output[0], ResponseCodeInterpreterToolCall)
    ):
        generated_code = result.raw_representation.raw_representation.output[0].code

        print(f"Generated code:\n{generated_code}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_with_code_interpreter_files.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
import tempfile

from agent_framework import ChatAgent, HostedCodeInterpreterTool
from agent_framework.openai import OpenAIResponsesClient
from openai import AsyncOpenAI

"""
OpenAI Responses Client with Code Interpreter and Files Example

This sample demonstrates using HostedCodeInterpreterTool with OpenAI Responses Client
for Python code execution and data analysis with uploaded files.
"""

# Helper functions


async def create_sample_file_and_upload(openai_client: AsyncOpenAI) -> tuple[str, str]:
    """Create a sample CSV file and upload it to OpenAI."""
    csv_data = """name,department,salary,years_experience
Alice Johnson,Engineering,95000,5
Bob Smith,Sales,75000,3
Carol Williams,Engineering,105000,8
David Brown,Marketing,68000,2
Emma Davis,Sales,82000,4
Frank Wilson,Engineering,88000,6
"""

    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as temp_file:
        temp_file.write(csv_data)
        temp_file_path = temp_file.name

    # Upload file to OpenAI
    print("Uploading file to OpenAI...")
    with open(temp_file_path, "rb") as file:
        uploaded_file = await openai_client.files.create(
            file=file,
            purpose="assistants",  # Required for code interpreter
        )

    print(f"File uploaded with ID: {uploaded_file.id}")
    return temp_file_path, uploaded_file.id


async def cleanup_files(openai_client: AsyncOpenAI, temp_file_path: str, file_id: str) -> None:
    """Clean up both local temporary file and uploaded file."""
    # Clean up: delete the uploaded file
    await openai_client.files.delete(file_id)
    print(f"Cleaned up uploaded file: {file_id}")

    # Clean up temporary local file
    os.unlink(temp_file_path)
    print(f"Cleaned up temporary file: {temp_file_path}")


async def main() -> None:
    """Complete example of uploading a file to OpenAI and using it with code interpreter."""
    print("=== OpenAI Code Interpreter with File Upload ===")

    openai_client = AsyncOpenAI()

    temp_file_path, file_id = await create_sample_file_and_upload(openai_client)

    # Create agent using OpenAI Responses client
    agent = ChatAgent(
        chat_client=OpenAIResponsesClient(),
        instructions="You are a helpful assistant that can analyze data files using Python code.",
        tools=HostedCodeInterpreterTool(inputs=[{"file_id": file_id}]),
    )

    # Test the code interpreter with the uploaded file
    query = "Analyze the employee data in the uploaded CSV file. Calculate average salary by department."
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Agent: {result.text}")

    await cleanup_files(openai_client, temp_file_path, file_id)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_with_explicit_settings.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIResponsesClient
from pydantic import Field

"""
OpenAI Responses Client with Explicit Settings Example

This sample demonstrates creating OpenAI Responses Client with explicit configuration
settings rather than relying on environment variable defaults.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    print("=== OpenAI Responses Client with Explicit Settings ===")

    agent = OpenAIResponsesClient(
        model_id=os.environ["OPENAI_RESPONSES_MODEL_ID"],
        api_key=os.environ["OPENAI_API_KEY"],
    ).create_agent(
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    result = await agent.run("What's the weather like in New York?")
    print(f"Result: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_with_file_search.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import HostedFileSearchTool, HostedVectorStoreContent
from agent_framework.openai import OpenAIResponsesClient

"""
OpenAI Responses Client with File Search Example

This sample demonstrates using HostedFileSearchTool with OpenAI Responses Client
for direct document-based question answering and information retrieval.
"""

# Helper functions


async def create_vector_store(client: OpenAIResponsesClient) -> tuple[str, HostedVectorStoreContent]:
    """Create a vector store with sample documents."""
    file = await client.client.files.create(
        file=("todays_weather.txt", b"The weather today is sunny with a high of 75F."), purpose="user_data"
    )
    vector_store = await client.client.vector_stores.create(
        name="knowledge_base",
        expires_after={"anchor": "last_active_at", "days": 1},
    )
    result = await client.client.vector_stores.files.create_and_poll(vector_store_id=vector_store.id, file_id=file.id)
    if result.last_error is not None:
        raise Exception(f"Vector store file processing failed with status: {result.last_error.message}")

    return file.id, HostedVectorStoreContent(vector_store_id=vector_store.id)


async def delete_vector_store(client: OpenAIResponsesClient, file_id: str, vector_store_id: str) -> None:
    """Delete the vector store after using it."""

    await client.client.vector_stores.delete(vector_store_id=vector_store_id)
    await client.client.files.delete(file_id=file_id)


async def main() -> None:
    client = OpenAIResponsesClient()

    message = "What is the weather today? Do a file search to find the answer."

    stream = False
    print(f"User: {message}")
    file_id, vector_store = await create_vector_store(client)
    if stream:
        print("Assistant: ", end="")
        async for chunk in client.get_streaming_response(
            message,
            tools=[HostedFileSearchTool(inputs=vector_store)],
            tool_choice="auto",
        ):
            if chunk.text:
                print(chunk.text, end="")
        print("")
    else:
        response = await client.get_response(
            message,
            tools=[HostedFileSearchTool(inputs=vector_store)],
            tool_choice="auto",
        )
        print(f"Assistant: {response}")
    await delete_vector_store(client, file_id, vector_store.vector_store_id)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_with_function_tools.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from datetime import datetime, timezone
from random import randint
from typing import Annotated

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient
from pydantic import Field

"""
OpenAI Responses Client with Function Tools Example

This sample demonstrates function tool integration with OpenAI Responses Client,
showing both agent-level and query-level tool configuration patterns.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


def get_time() -> str:
    """Get the current UTC time."""
    current_time = datetime.now(timezone.utc)
    return f"The current UTC time is {current_time.strftime('%Y-%m-%d %H:%M:%S')}."


async def tools_on_agent_level() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    agent = ChatAgent(
        chat_client=OpenAIResponsesClient(),
        instructions="You are a helpful assistant that can provide weather and time information.",
        tools=[get_weather, get_time],  # Tools defined at agent creation
    )

    # First query - agent can use weather tool
    query1 = "What's the weather like in New York?"
    print(f"User: {query1}")
    result1 = await agent.run(query1)
    print(f"Agent: {result1}\n")

    # Second query - agent can use time tool
    query2 = "What's the current UTC time?"
    print(f"User: {query2}")
    result2 = await agent.run(query2)
    print(f"Agent: {result2}\n")

    # Third query - agent can use both tools if needed
    query3 = "What's the weather in London and what's the current UTC time?"
    print(f"User: {query3}")
    result3 = await agent.run(query3)
    print(f"Agent: {result3}\n")


async def tools_on_run_level() -> None:
    """Example showing tools passed to the run method."""
    print("=== Tools Passed to Run Method ===")

    # Agent created without tools
    agent = ChatAgent(
        chat_client=OpenAIResponsesClient(),
        instructions="You are a helpful assistant.",
        # No tools defined here
    )

    # First query with weather tool
    query1 = "What's the weather like in Seattle?"
    print(f"User: {query1}")
    result1 = await agent.run(query1, tools=[get_weather])  # Tool passed to run method
    print(f"Agent: {result1}\n")

    # Second query with time tool
    query2 = "What's the current UTC time?"
    print(f"User: {query2}")
    result2 = await agent.run(query2, tools=[get_time])  # Different tool for this query
    print(f"Agent: {result2}\n")

    # Third query with multiple tools
    query3 = "What's the weather in Chicago and what's the current UTC time?"
    print(f"User: {query3}")
    result3 = await agent.run(query3, tools=[get_weather, get_time])  # Multiple tools
    print(f"Agent: {result3}\n")


async def mixed_tools_example() -> None:
    """Example showing both agent-level tools and run-method tools."""
    print("=== Mixed Tools Example (Agent + Run Method) ===")

    # Agent created with some base tools
    agent = ChatAgent(
        chat_client=OpenAIResponsesClient(),
        instructions="You are a comprehensive assistant that can help with various information requests.",
        tools=[get_weather],  # Base tool available for all queries
    )

    # Query using both agent tool and additional run-method tools
    query = "What's the weather in Denver and what's the current UTC time?"
    print(f"User: {query}")

    # Agent has access to get_weather (from creation) + additional tools from run method
    result = await agent.run(
        query,
        tools=[get_time],  # Additional tools for this specific query
    )
    print(f"Agent: {result}\n")


async def main() -> None:
    print("=== OpenAI Responses Client Agent with Function Tools Examples ===\n")

    await tools_on_agent_level()
    await tools_on_run_level()
    await mixed_tools_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_with_hosted_mcp.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import TYPE_CHECKING, Any

from agent_framework import ChatAgent, HostedMCPTool
from agent_framework.openai import OpenAIResponsesClient

"""
OpenAI Responses Client with Hosted MCP Example

This sample demonstrates integrating hosted Model Context Protocol (MCP) tools with
OpenAI Responses Client, including user approval workflows for function call security.
"""

if TYPE_CHECKING:
    from agent_framework import AgentProtocol, AgentThread


async def handle_approvals_without_thread(query: str, agent: "AgentProtocol"):
    """When we don't have a thread, we need to ensure we return with the input, approval request and approval."""
    from agent_framework import ChatMessage

    result = await agent.run(query)
    while len(result.user_input_requests) > 0:
        new_inputs: list[Any] = [query]
        for user_input_needed in result.user_input_requests:
            print(
                f"User Input Request for function from {agent.name}: {user_input_needed.function_call.name}"
                f" with arguments: {user_input_needed.function_call.arguments}"
            )
            new_inputs.append(ChatMessage(role="assistant", contents=[user_input_needed]))
            user_approval = input("Approve function call? (y/n): ")
            new_inputs.append(
                ChatMessage(role="user", contents=[user_input_needed.create_response(user_approval.lower() == "y")])
            )

        result = await agent.run(new_inputs)
    return result


async def handle_approvals_with_thread(query: str, agent: "AgentProtocol", thread: "AgentThread"):
    """Here we let the thread deal with the previous responses, and we just rerun with the approval."""
    from agent_framework import ChatMessage

    result = await agent.run(query, thread=thread, store=True)
    while len(result.user_input_requests) > 0:
        new_input: list[Any] = []
        for user_input_needed in result.user_input_requests:
            print(
                f"User Input Request for function from {agent.name}: {user_input_needed.function_call.name}"
                f" with arguments: {user_input_needed.function_call.arguments}"
            )
            user_approval = input("Approve function call? (y/n): ")
            new_input.append(
                ChatMessage(
                    role="user",
                    contents=[user_input_needed.create_response(user_approval.lower() == "y")],
                )
            )
        result = await agent.run(new_input, thread=thread, store=True)
    return result


async def handle_approvals_with_thread_streaming(query: str, agent: "AgentProtocol", thread: "AgentThread"):
    """Here we let the thread deal with the previous responses, and we just rerun with the approval."""
    from agent_framework import ChatMessage

    new_input: list[ChatMessage] = []
    new_input_added = True
    while new_input_added:
        new_input_added = False
        new_input.append(ChatMessage(role="user", text=query))
        async for update in agent.run_stream(new_input, thread=thread, store=True):
            if update.user_input_requests:
                for user_input_needed in update.user_input_requests:
                    print(
                        f"User Input Request for function from {agent.name}: {user_input_needed.function_call.name}"
                        f" with arguments: {user_input_needed.function_call.arguments}"
                    )
                    user_approval = input("Approve function call? (y/n): ")
                    new_input.append(
                        ChatMessage(
                            role="user", contents=[user_input_needed.create_response(user_approval.lower() == "y")]
                        )
                    )
                    new_input_added = True
            else:
                yield update


async def run_hosted_mcp_without_thread_and_specific_approval() -> None:
    """Example showing Mcp Tools with approvals without using a thread."""
    print("=== Mcp with approvals and without thread ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    async with ChatAgent(
        chat_client=OpenAIResponsesClient(),
        name="DocsAgent",
        instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        tools=HostedMCPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            # we don't require approval for microsoft_docs_search tool calls
            # but we do for any other tool
            approval_mode={"never_require_approval": ["microsoft_docs_search"]},
        ),
    ) as agent:
        # First query
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        result1 = await handle_approvals_without_thread(query1, agent)
        print(f"{agent.name}: {result1}\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        result2 = await handle_approvals_without_thread(query2, agent)
        print(f"{agent.name}: {result2}\n")


async def run_hosted_mcp_without_approval() -> None:
    """Example showing Mcp Tools without approvals."""
    print("=== Mcp without approvals ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    async with ChatAgent(
        chat_client=OpenAIResponsesClient(),
        name="DocsAgent",
        instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        tools=HostedMCPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            # we don't require approval for any function calls
            # this means we will not see the approval messages,
            # it is fully handled by the service and a final response is returned.
            approval_mode="never_require",
        ),
    ) as agent:
        # First query
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        result1 = await handle_approvals_without_thread(query1, agent)
        print(f"{agent.name}: {result1}\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        result2 = await handle_approvals_without_thread(query2, agent)
        print(f"{agent.name}: {result2}\n")


async def run_hosted_mcp_with_thread() -> None:
    """Example showing Mcp Tools with approvals using a thread."""
    print("=== Mcp with approvals and with thread ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    async with ChatAgent(
        chat_client=OpenAIResponsesClient(),
        name="DocsAgent",
        instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        tools=HostedMCPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            # we require approval for all function calls
            approval_mode="always_require",
        ),
    ) as agent:
        # First query
        thread = agent.get_new_thread()
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        result1 = await handle_approvals_with_thread(query1, agent, thread)
        print(f"{agent.name}: {result1}\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        result2 = await handle_approvals_with_thread(query2, agent, thread)
        print(f"{agent.name}: {result2}\n")


async def run_hosted_mcp_with_thread_streaming() -> None:
    """Example showing Mcp Tools with approvals using a thread."""
    print("=== Mcp with approvals and with thread ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    async with ChatAgent(
        chat_client=OpenAIResponsesClient(),
        name="DocsAgent",
        instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        tools=HostedMCPTool(
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
            # we require approval for all function calls
            approval_mode="always_require",
        ),
    ) as agent:
        # First query
        thread = agent.get_new_thread()
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        print(f"{agent.name}: ", end="")
        async for update in handle_approvals_with_thread_streaming(query1, agent, thread):
            print(update, end="")
        print("\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        print(f"{agent.name}: ", end="")
        async for update in handle_approvals_with_thread_streaming(query2, agent, thread):
            print(update, end="")
        print("\n")


async def main() -> None:
    print("=== OpenAI Responses Client Agent with Hosted Mcp Tools Examples ===\n")

    await run_hosted_mcp_without_approval()
    await run_hosted_mcp_without_thread_and_specific_approval()
    await run_hosted_mcp_with_thread()
    await run_hosted_mcp_with_thread_streaming()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_with_local_mcp.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.openai import OpenAIResponsesClient

"""
OpenAI Responses Client with Local MCP Example

This sample demonstrates integrating local Model Context Protocol (MCP) tools with
OpenAI Responses Client for direct response generation with external capabilities.
"""


async def streaming_with_mcp(show_raw_stream: bool = False) -> None:
    """Example showing tools defined when creating the agent.

    If you want to access the full stream of events that has come from the model, you can access it,
    through the raw_representation. You can view this, by setting the show_raw_stream parameter to True.
    """
    print("=== Tools Defined on Agent Level ===")
    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    async with ChatAgent(
        chat_client=OpenAIResponsesClient(),
        name="DocsAgent",
        instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        tools=MCPStreamableHTTPTool(  # Tools defined at agent creation
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
        ),
    ) as agent:
        # First query
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        print(f"{agent.name}: ", end="")
        async for chunk in agent.run_stream(query1):
            if show_raw_stream:
                print("Streamed event: ", chunk.raw_representation.raw_representation)  # type:ignore
            elif chunk.text:
                print(chunk.text, end="")
        print("")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        print(f"{agent.name}: ", end="")
        async for chunk in agent.run_stream(query2):
            if show_raw_stream:
                print("Streamed event: ", chunk.raw_representation.raw_representation)  # type:ignore
            elif chunk.text:
                print(chunk.text, end="")
        print("\n\n")


async def run_with_mcp() -> None:
    """Example showing tools defined when creating the agent."""
    print("=== Tools Defined on Agent Level ===")

    # Tools are provided when creating the agent
    # The agent can use these tools for any query during its lifetime
    async with ChatAgent(
        chat_client=OpenAIResponsesClient(),
        name="DocsAgent",
        instructions="You are a helpful assistant that can help with microsoft documentation questions.",
        tools=MCPStreamableHTTPTool(  # Tools defined at agent creation
            name="Microsoft Learn MCP",
            url="https://learn.microsoft.com/api/mcp",
        ),
    ) as agent:
        # First query
        query1 = "How to create an Azure storage account using az cli?"
        print(f"User: {query1}")
        result1 = await agent.run(query1)
        print(f"{agent.name}: {result1}\n")
        print("\n=======================================\n")
        # Second query
        query2 = "What is Microsoft Agent Framework?"
        print(f"User: {query2}")
        result2 = await agent.run(query2)
        print(f"{agent.name}: {result2}\n")


async def main() -> None:
    print("=== OpenAI Responses Client Agent with Function Tools Examples ===\n")

    await run_with_mcp()
    await streaming_with_mcp()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_with_structured_output.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import AgentRunResponse
from agent_framework.openai import OpenAIResponsesClient
from pydantic import BaseModel

"""
OpenAI Responses Client with Structured Output Example

This sample demonstrates using structured output capabilities with OpenAI Responses Client,
showing Pydantic model integration for type-safe response parsing and data extraction.
"""


class OutputStruct(BaseModel):
    """A structured output for testing purposes."""

    city: str
    description: str


async def non_streaming_example() -> None:
    print("=== Non-streaming example ===")

    # Create an OpenAI Responses agent
    agent = OpenAIResponsesClient().create_agent(
        name="CityAgent",
        instructions="You are a helpful agent that describes cities in a structured format.",
    )

    # Ask the agent about a city
    query = "Tell me about Paris, France"
    print(f"User: {query}")

    # Get structured response from the agent using response_format parameter
    result = await agent.run(query, response_format=OutputStruct)

    # Access the structured output directly from the response value
    if result.value:
        structured_data: OutputStruct = result.value  # type: ignore
        print("Structured Output Agent (from result.value):")
        print(f"City: {structured_data.city}")
        print(f"Description: {structured_data.description}")
    else:
        print("Error: No structured data found in result.value")


async def streaming_example() -> None:
    print("=== Streaming example ===")

    # Create an OpenAI Responses agent
    agent = OpenAIResponsesClient().create_agent(
        name="CityAgent",
        instructions="You are a helpful agent that describes cities in a structured format.",
    )

    # Ask the agent about a city
    query = "Tell me about Tokyo, Japan"
    print(f"User: {query}")

    # Get structured response from streaming agent using AgentRunResponse.from_agent_response_generator
    # This method collects all streaming updates and combines them into a single AgentRunResponse
    result = await AgentRunResponse.from_agent_response_generator(
        agent.run_stream(query, response_format=OutputStruct),
        output_format_type=OutputStruct,
    )

    # Access the structured output directly from the response value
    if result.value:
        structured_data: OutputStruct = result.value  # type: ignore
        print("Structured Output (from streaming with AgentRunResponse.from_agent_response_generator):")
        print(f"City: {structured_data.city}")
        print(f"Description: {structured_data.description}")
    else:
        print("Error: No structured data found in result.value")


async def main() -> None:
    print("=== OpenAI Responses Agent with Structured Output ===")

    await non_streaming_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_with_thread.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework import AgentThread, ChatAgent
from agent_framework.openai import OpenAIResponsesClient
from pydantic import Field

"""
OpenAI Responses Client with Thread Management Example

This sample demonstrates thread management with OpenAI Responses Client, showing
persistent conversation context and simplified response handling.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def example_with_automatic_thread_creation() -> None:
    """Example showing automatic thread creation."""
    print("=== Automatic Thread Creation Example ===")

    agent = ChatAgent(
        chat_client=OpenAIResponsesClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # First conversation - no thread provided, will be created automatically
    query1 = "What's the weather like in Seattle?"
    print(f"User: {query1}")
    result1 = await agent.run(query1)
    print(f"Agent: {result1.text}")

    # Second conversation - still no thread provided, will create another new thread
    query2 = "What was the last city I asked about?"
    print(f"\nUser: {query2}")
    result2 = await agent.run(query2)
    print(f"Agent: {result2.text}")
    print("Note: Each call creates a separate thread, so the agent doesn't remember previous context.\n")


async def example_with_thread_persistence_in_memory() -> None:
    """
    Example showing thread persistence across multiple conversations.
    In this example, messages are stored in-memory.
    """
    print("=== Thread Persistence Example (In-Memory) ===")

    agent = ChatAgent(
        chat_client=OpenAIResponsesClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # Create a new thread that will be reused
    thread = agent.get_new_thread()

    # First conversation
    query1 = "What's the weather like in Tokyo?"
    print(f"User: {query1}")
    result1 = await agent.run(query1, thread=thread)
    print(f"Agent: {result1.text}")

    # Second conversation using the same thread - maintains context
    query2 = "How about London?"
    print(f"\nUser: {query2}")
    result2 = await agent.run(query2, thread=thread)
    print(f"Agent: {result2.text}")

    # Third conversation - agent should remember both previous cities
    query3 = "Which of the cities I asked about has better weather?"
    print(f"\nUser: {query3}")
    result3 = await agent.run(query3, thread=thread)
    print(f"Agent: {result3.text}")
    print("Note: The agent remembers context from previous messages in the same thread.\n")


async def example_with_existing_thread_id() -> None:
    """
    Example showing how to work with an existing thread ID from the service.
    In this example, messages are stored on the server using OpenAI conversation state.
    """
    print("=== Existing Thread ID Example ===")

    # First, create a conversation and capture the thread ID
    existing_thread_id = None

    agent = ChatAgent(
        chat_client=OpenAIResponsesClient(),
        instructions="You are a helpful weather agent.",
        tools=get_weather,
    )

    # Start a conversation and get the thread ID
    thread = agent.get_new_thread()

    query1 = "What's the weather in Paris?"
    print(f"User: {query1}")
    # Enable OpenAI conversation state by setting `store` parameter to True
    result1 = await agent.run(query1, thread=thread, store=True)
    print(f"Agent: {result1.text}")

    # The thread ID is set after the first response
    existing_thread_id = thread.service_thread_id
    print(f"Thread ID: {existing_thread_id}")

    if existing_thread_id:
        print("\n--- Continuing with the same thread ID in a new agent instance ---")

        agent = ChatAgent(
            chat_client=OpenAIResponsesClient(),
            instructions="You are a helpful weather agent.",
            tools=get_weather,
        )

        # Create a thread with the existing ID
        thread = AgentThread(service_thread_id=existing_thread_id)

        query2 = "What was the last city I asked about?"
        print(f"User: {query2}")
        result2 = await agent.run(query2, thread=thread, store=True)
        print(f"Agent: {result2.text}")
        print("Note: The agent continues the conversation from the previous thread by using thread ID.\n")


async def main() -> None:
    print("=== OpenAI Response Client Agent Thread Management Examples ===\n")

    await example_with_automatic_thread_creation()
    await example_with_thread_persistence_in_memory()
    await example_with_existing_thread_id()


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/openai/openai_responses_client_with_web_search.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import HostedWebSearchTool
from agent_framework.openai import OpenAIResponsesClient

"""
OpenAI Responses Client with Web Search Example

This sample demonstrates using HostedWebSearchTool with OpenAI Responses Client
for direct real-time information retrieval and current data access.
"""


async def main() -> None:
    client = OpenAIResponsesClient()

    message = "What is the current weather? Do not ask for my current location."
    # Test that the client will use the web search tool with location
    additional_properties = {
        "user_location": {
            "country": "US",
            "city": "Seattle",
        }
    }
    stream = False
    print(f"User: {message}")
    if stream:
        print("Assistant: ", end="")
        async for chunk in client.get_streaming_response(
            message,
            tools=[HostedWebSearchTool(additional_properties=additional_properties)],
            tool_choice="auto",
        ):
            if chunk.text:
                print(chunk.text, end="")
        print("")
    else:
        response = await client.get_response(
            message,
            tools=[HostedWebSearchTool(additional_properties=additional_properties)],
            tool_choice="auto",
        )
        print(f"Assistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/agents/resources/countries.json
================================================
{
  "openapi": "3.0.1",
  "info": {
    "title": "REST Countries API",
    "description": "Get information about countries of the world",
    "version": "3.1"
  },
  "servers": [
    {
      "url": "https://restcountries.com/v3.1"
    }
  ],
  "paths": {
    "/currency/{currency}": {
      "get": {
        "operationId": "getCountriesByCurrency",
        "summary": "Get countries by currency",
        "description": "Search for countries by currency code",
        "parameters": [
          {
            "name": "currency",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string"
            },
            "description": "Currency code (e.g., THB, USD, EUR)"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "name": {
                        "type": "object",
                        "properties": {
                          "common": {"type": "string"},
                          "official": {"type": "string"}
                        }
                      },
                      "population": {"type": "integer"},
                      "region": {"type": "string"},
                      "subregion": {"type": "string"},
                      "capital": {
                        "type": "array",
                        "items": {"type": "string"}
                      },
                      "currencies": {
                        "type": "object",
                        "additionalProperties": {
                          "type": "object",
                          "properties": {
                            "name": {"type": "string"},
                            "symbol": {"type": "string"}
                          }
                        }
                      },
                      "languages": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                      },
                      "latlng": {
                        "type": "array",
                        "items": {"type": "number"}
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/name/{name}": {
      "get": {
        "operationId": "getCountryByName",
        "summary": "Get country by name",
        "description": "Search for countries by name",
        "parameters": [
          {
            "name": "name",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string"
            },
            "description": "Country name"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "name": {
                        "type": "object",
                        "properties": {
                          "common": {"type": "string"},
                          "official": {"type": "string"}
                        }
                      },
                      "population": {"type": "integer"},
                      "region": {"type": "string"},
                      "subregion": {"type": "string"},
                      "capital": {
                        "type": "array",
                        "items": {"type": "string"}
                      },
                      "currencies": {
                        "type": "object",
                        "additionalProperties": {
                          "type": "object",
                          "properties": {
                            "name": {"type": "string"},
                            "symbol": {"type": "string"}
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}


================================================
FILE: python/samples/getting_started/agents/resources/weather.json
================================================
{
  "openapi": "3.1.0",
  "info": {
    "title": "wttr.in Weather API",
    "description": "Retrieves current weather data for a location using wttr.in service",
    "version": "v1.0.0"
  },
  "servers": [
    {
      "url": "https://wttr.in"
    }
  ],
  "paths": {
    "/{location}": {
      "get": {
        "operationId": "GetCurrentWeather",
        "summary": "Get weather information for a specific location",
        "description": "Get weather information for a specific location",
        "parameters": [
          {
            "name": "location",
            "in": "path",
            "description": "City or location to retrieve the weather for",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "format",
            "in": "query",
            "description": "Format in which to return data. Always use 3.",
            "required": true,
            "schema": {
              "type": "integer",
              "default": 3
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "text/plain": {
                "schema": {
                  "type": "string"
                }
              }
            }
          },
          "404": {
            "description": "Location not found"
          }
        },
        "deprecated": false
      }
    }
  },
  "components": {
    "schemas": {}
  }
}


================================================
FILE: python/samples/getting_started/chat_client/README.md
================================================
# Chat Client Examples

This folder contains simple examples demonstrating direct usage of various chat clients.

## Examples

| File | Description |
|------|-------------|
| [`azure_assistants_client.py`](azure_assistants_client.py) | Direct usage of Azure Assistants Client for basic chat interactions with Azure OpenAI assistants. |
| [`azure_chat_client.py`](azure_chat_client.py) | Direct usage of Azure Chat Client for chat interactions with Azure OpenAI models. |
| [`azure_responses_client.py`](azure_responses_client.py) | Direct usage of Azure Responses Client for structured response generation with Azure OpenAI models. |
| [`chat_response_cancellation.py`](chat_response_cancellation.py) | Demonstrates how to cancel chat responses during streaming, showing proper cancellation handling and cleanup. |
| [`azure_ai_chat_client.py`](azure_ai_chat_client.py) | Direct usage of Azure AI Chat Client for chat interactions with Azure AI models. |
| [`openai_assistants_client.py`](openai_assistants_client.py) | Direct usage of OpenAI Assistants Client for basic chat interactions with OpenAI assistants. |
| [`openai_chat_client.py`](openai_chat_client.py) | Direct usage of OpenAI Chat Client for chat interactions with OpenAI models. |
| [`openai_responses_client.py`](openai_responses_client.py) | Direct usage of OpenAI Responses Client for structured response generation with OpenAI models. |

## Environment Variables

Depending on which client you're using, set the appropriate environment variables:

**For Azure clients:**
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`: The name of your Azure OpenAI chat deployment
- `AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME`: The name of your Azure OpenAI responses deployment

**For Azure AI client:**
- `AZURE_AI_PROJECT_ENDPOINT`: Your Azure AI project endpoint
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`: The name of your model deployment

**For OpenAI clients:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_CHAT_MODEL_ID`: The OpenAI model to use for chat clients (e.g., `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`)
- `OPENAI_RESPONSES_MODEL_ID`: The OpenAI model to use for responses clients (e.g., `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`)



================================================
FILE: python/samples/getting_started/chat_client/azure_ai_chat_client.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field

"""
Azure AI Chat Client Direct Usage Example

Demonstrates direct AzureAIChatClient usage for chat interactions with Azure AI models.
Shows function calling capabilities with custom business logic.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with AzureAIAgentClient(async_credential=AzureCliCredential()) as client:
        message = "What's the weather in Amsterdam and in Paris?"
        stream = False
        print(f"User: {message}")
        if stream:
            print("Assistant: ", end="")
            async for chunk in client.get_streaming_response(message, tools=get_weather):
                if str(chunk):
                    print(str(chunk), end="")
            print("")
        else:
            response = await client.get_response(message, tools=get_weather)
            print(f"Assistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/chat_client/azure_assistants_client.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.azure import AzureOpenAIAssistantsClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure Assistants Client Direct Usage Example

Demonstrates direct AzureAssistantsClient usage for chat interactions with Azure OpenAI assistants.
Shows function calling capabilities and automatic assistant creation.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    async with AzureOpenAIAssistantsClient(credential=AzureCliCredential()) as client:
        message = "What's the weather in Amsterdam and in Paris?"
        stream = False
        print(f"User: {message}")
        if stream:
            print("Assistant: ", end="")
            async for chunk in client.get_streaming_response(message, tools=get_weather):
                if str(chunk):
                    print(str(chunk), end="")
            print("")
        else:
            response = await client.get_response(message, tools=get_weather)
            print(f"Assistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/chat_client/azure_chat_client.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from pydantic import Field

"""
Azure Chat Client Direct Usage Example

Demonstrates direct AzureChatClient usage for chat interactions with Azure OpenAI models.
Shows function calling capabilities with custom business logic.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    client = AzureOpenAIChatClient(credential=AzureCliCredential())
    message = "What's the weather in Amsterdam and in Paris?"
    stream = False
    print(f"User: {message}")
    if stream:
        print("Assistant: ", end="")
        async for chunk in client.get_streaming_response(message, tools=get_weather):
            if str(chunk):
                print(str(chunk), end="")
        print("")
    else:
        response = await client.get_response(message, tools=get_weather)
        print(f"Assistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/chat_client/azure_responses_client.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework import ChatResponse
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from pydantic import BaseModel, Field

"""
Azure Responses Client Direct Usage Example

Demonstrates direct AzureResponsesClient usage for structured response generation with Azure OpenAI models.
Shows function calling capabilities with custom business logic.
"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


class OutputStruct(BaseModel):
    """Structured output for weather information."""

    location: str
    weather: str


async def main() -> None:
    # For authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    client = AzureOpenAIResponsesClient(credential=AzureCliCredential())
    message = "What's the weather in Amsterdam and in Paris?"
    stream = True
    print(f"User: {message}")
    if stream:
        response = await ChatResponse.from_chat_response_generator(
            client.get_streaming_response(message, tools=get_weather, response_format=OutputStruct),
            output_format_type=OutputStruct,
        )
        print(f"Assistant: {response.value}")

    else:
        response = await client.get_response(message, tools=get_weather, response_format=OutputStruct)
        print(f"Assistant: {response.value}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/chat_client/chat_response_cancellation.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework.openai import OpenAIChatClient

"""
Chat Response Cancellation Example

Demonstrates proper cancellation of streaming chat responses during execution.
Shows asyncio task cancellation and resource cleanup techniques.
"""


async def main() -> None:
    """
    Demonstrates cancelling a chat request after 1 second.
    Creates a task for the chat request, waits briefly, then cancels it to show proper cleanup.

    Configuration:
    - OpenAI model ID: Use "model_id" parameter or "OPENAI_CHAT_MODEL_ID" environment variable
    - OpenAI API key: Use "api_key" parameter or "OPENAI_API_KEY" environment variable
    """
    chat_client = OpenAIChatClient()

    try:
        task = asyncio.create_task(chat_client.get_response(messages=["Tell me a fantasy story."]))
        await asyncio.sleep(1)
        task.cancel()
        await task
    except asyncio.CancelledError:
        print("Request was cancelled")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/chat_client/openai_assistants_client.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIAssistantsClient
from pydantic import Field

"""
OpenAI Assistants Client Direct Usage Example

Demonstrates direct OpenAIAssistantsClient usage for chat interactions with OpenAI assistants.
Shows function calling capabilities and automatic assistant creation.

"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    async with OpenAIAssistantsClient() as client:
        message = "What's the weather in Amsterdam and in Paris?"
        stream = False
        print(f"User: {message}")
        if stream:
            print("Assistant: ", end="")
            async for chunk in client.get_streaming_response(message, tools=get_weather):
                if str(chunk):
                    print(str(chunk), end="")
            print("")
        else:
            response = await client.get_response(message, tools=get_weather)
            print(f"Assistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/chat_client/openai_chat_client.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIChatClient
from pydantic import Field

"""
OpenAI Chat Client Direct Usage Example

Demonstrates direct OpenAIChatClient usage for chat interactions with OpenAI models.
Shows function calling capabilities with custom business logic.

"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    client = OpenAIChatClient()
    message = "What's the weather in Amsterdam and in Paris?"
    stream = True
    print(f"User: {message}")
    if stream:
        print("Assistant: ", end="")
        async for chunk in client.get_streaming_response(message, tools=get_weather):
            if chunk.text:
                print(chunk.text, end="")
        print("")
    else:
        response = await client.get_response(message, tools=get_weather)
        print(f"Assistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/chat_client/openai_responses_client.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from random import randint
from typing import Annotated

from agent_framework.openai import OpenAIResponsesClient
from pydantic import Field

"""
OpenAI Responses Client Direct Usage Example

Demonstrates direct OpenAIResponsesClient usage for structured response generation with OpenAI models.
Shows function calling capabilities with custom business logic.

"""


def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


async def main() -> None:
    client = OpenAIResponsesClient()
    message = "What's the weather in Amsterdam and in Paris?"
    stream = False
    print(f"User: {message}")
    if stream:
        print("Assistant: ", end="")
        async for chunk in client.get_streaming_response(message, tools=get_weather):
            if chunk.text:
                print(chunk.text, end="")
        print("")
    else:
        response = await client.get_response(message, tools=get_weather)
        print(f"Assistant: {response}")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/context_providers/simple_context_provider.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
from collections.abc import MutableSequence, Sequence
from typing import Any

from agent_framework import ChatAgent, ChatClientProtocol, ChatMessage, ChatOptions, Context, ContextProvider
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from pydantic import BaseModel


class UserInfo(BaseModel):
    name: str | None = None
    age: int | None = None


class UserInfoMemory(ContextProvider):
    def __init__(self, chat_client: ChatClientProtocol, user_info: UserInfo | None = None, **kwargs: Any):
        """Create the memory.

        If you pass in kwargs, they will be attempted to be used to create a UserInfo object.
        """

        self._chat_client = chat_client
        if user_info:
            self.user_info = user_info
        elif kwargs:
            self.user_info = UserInfo.model_validate(kwargs)
        else:
            self.user_info = UserInfo()

    async def invoked(
        self,
        request_messages: ChatMessage | Sequence[ChatMessage],
        response_messages: ChatMessage | Sequence[ChatMessage] | None = None,
        invoke_exception: Exception | None = None,
        **kwargs: Any,
    ) -> None:
        """Extract user information from messages after each agent call."""
        # Check if we need to extract user info from user messages
        user_messages = [msg for msg in request_messages if hasattr(msg, "role") and msg.role.value == "user"]  # type: ignore

        if (self.user_info.name is None or self.user_info.age is None) and user_messages:
            try:
                # Use the chat client to extract structured information
                result = await self._chat_client.get_response(
                    messages=request_messages,  # type: ignore
                    chat_options=ChatOptions(
                        instructions="Extract the user's name and age from the message if present. If not present return nulls.",
                        response_format=UserInfo,
                    ),
                )

                # Update user info with extracted data
                if result.value and isinstance(result.value, UserInfo):
                    if self.user_info.name is None and result.value.name:
                        self.user_info.name = result.value.name
                    if self.user_info.age is None and result.value.age:
                        self.user_info.age = result.value.age

            except Exception:
                pass  # Failed to extract, continue without updating

    async def invoking(self, messages: ChatMessage | MutableSequence[ChatMessage], **kwargs: Any) -> Context:
        """Provide user information context before each agent call."""
        instructions: list[str] = []

        if self.user_info.name is None:
            instructions.append(
                "Ask the user for their name and politely decline to answer any questions until they provide it."
            )
        else:
            instructions.append(f"The user's name is {self.user_info.name}.")

        if self.user_info.age is None:
            instructions.append(
                "Ask the user for their age and politely decline to answer any questions until they provide it."
            )
        else:
            instructions.append(f"The user's age is {self.user_info.age}.")

        # Return context with additional instructions
        return Context(instructions=" ".join(instructions))

    def serialize(self) -> str:
        """Serialize the user info for thread persistence."""
        return self.user_info.model_dump_json()


async def main():
    async with AzureCliCredential() as credential:
        chat_client = AzureAIAgentClient(async_credential=credential)

        # Create the memory provider
        memory_provider = UserInfoMemory(chat_client)

        # Create the agent with memory
        async with ChatAgent(
            chat_client=chat_client,
            instructions="You are a friendly assistant. Always address the user by their name.",
            context_providers=memory_provider,
        ) as agent:
            # Create a new thread for the conversation
            thread = agent.get_new_thread()

            print(await agent.run("Hello, what is the square root of 9?", thread=thread))
            print(await agent.run("My name is Ruaidhrí", thread=thread))
            print(await agent.run("I am 20 years old", thread=thread))

            # Access the memory component via the thread's get_service method and inspect the memories
            user_info_memory = thread.context_provider.providers[0]  # type: ignore
            if user_info_memory:
                print()
                print(f"MEMORY - User Name: {user_info_memory.user_info.name}")  # type: ignore
                print(f"MEMORY - User Age: {user_info_memory.user_info.age}")  # type: ignore


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/context_providers/mem0/README.md
================================================
# Mem0 Context Provider Examples

[Mem0](https://mem0.ai/) is a self-improving memory layer for Large Language Models that enables applications to have long-term memory capabilities. The Agent Framework's Mem0 context provider integrates with Mem0's API to provide persistent memory across conversation sessions.

This folder contains examples demonstrating how to use the Mem0 context provider with the Agent Framework for persistent memory and context management across conversations.

## Examples

| File | Description |
|------|-------------|
| [`mem0_basic.py`](mem0_basic.py) | Basic example of using Mem0 context provider to store and retrieve user preferences across different conversation threads. |
| [`mem0_threads.py`](mem0_threads.py) | Advanced example demonstrating different thread scoping strategies with Mem0. Covers global thread scope (memories shared across all operations), per-operation thread scope (memories isolated per thread), and multiple agents with different memory configurations for personal vs. work contexts. |
| [`mem0_oss.py`](mem0_oss.py) | Example of using the Mem0 Open Source self-hosted version as the context provider. Demonstrates setup and configuration for local deployment. |

## Prerequisites

### Required Resources

1. [Mem0 API Key](https://app.mem0.ai/) - Sign up for a Mem0 account and get your API key - _or_ self-host [Mem0 Open Source](https://docs.mem0.ai/open-source/overview)
2. Azure AI project endpoint (used in these examples)
3. Azure CLI authentication (run `az login`)

## Configuration

### Environment Variables

Set the following environment variables:

**For Mem0 Platform:**
- `MEM0_API_KEY`: Your Mem0 API key (alternatively, pass it as `api_key` parameter to `Mem0Provider`). Not required if you are self-hosting [Mem0 Open Source](https://docs.mem0.ai/open-source/overview)

**For Mem0 Open Source:**
- `OPENAI_API_KEY`: Your OpenAI API key (used by Mem0 OSS for embedding generation and automatic memory extraction)

**For Azure AI:**
- `AZURE_AI_PROJECT_ENDPOINT`: Your Azure AI project endpoint
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`: The name of your model deployment

## Key Concepts

### Memory Scoping

The Mem0 context provider supports different scoping strategies:

- **Global Scope** (`scope_to_per_operation_thread_id=False`): Memories are shared across all conversation threads
- **Thread Scope** (`scope_to_per_operation_thread_id=True`): Memories are isolated per conversation thread

### Memory Association

Mem0 records can be associated with different identifiers:

- `user_id`: Associate memories with a specific user
- `agent_id`: Associate memories with a specific agent
- `thread_id`: Associate memories with a specific conversation thread
- `application_id`: Associate memories with an application context



================================================
FILE: python/samples/getting_started/context_providers/mem0/mem0_basic.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import uuid

from agent_framework.azure import AzureAIAgentClient
from agent_framework.mem0 import Mem0Provider
from azure.identity.aio import AzureCliCredential


def retrieve_company_report(company_code: str, detailed: bool) -> str:
    if company_code != "CNTS":
        raise ValueError("Company code not found")
    if not detailed:
        return "CNTS is a company that specializes in technology."
    return (
        "CNTS is a company that specializes in technology. "
        "It had a revenue of $10 million in 2022. It has 100 employees."
    )


async def main() -> None:
    """Example of memory usage with Mem0 context provider."""
    print("=== Mem0 Context Provider Example ===")

    # Each record in Mem0 should be associated with agent_id or user_id or application_id or thread_id.
    # In this example, we associate Mem0 records with user_id.
    user_id = str(uuid.uuid4())

    # For Azure authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    # For Mem0 authentication, set Mem0 API key via "api_key" parameter or MEM0_API_KEY environment variable.
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="FriendlyAssistant",
            instructions="You are a friendly assistant.",
            tools=retrieve_company_report,
            context_providers=Mem0Provider(user_id=user_id),
        ) as agent,
    ):
        # First ask the agent to retrieve a company report with no previous context.
        # The agent will not be able to invoke the tool, since it doesn't know
        # the company code or the report format, so it should ask for clarification.
        query = "Please retrieve my company report"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")

        # Now tell the agent the company code and the report format that you want to use
        # and it should be able to invoke the tool and return the report.
        query = "I always work with CNTS and I always want a detailed report format. Please remember and retrieve it."
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")

        print("\nRequest within a new thread:")
        # Create a new thread for the agent.
        # The new thread has no context of the previous conversation.
        thread = agent.get_new_thread()

        # Since we have the mem0 component in the thread, the agent should be able to
        # retrieve the company report without asking for clarification, as it will
        # be able to remember the user preferences from Mem0 component.
        query = "Please retrieve my company report"
        print(f"User: {query}")
        result = await agent.run(query, thread=thread)
        print(f"Agent: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/context_providers/mem0/mem0_oss.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import uuid

from agent_framework.azure import AzureAIAgentClient
from agent_framework.mem0 import Mem0Provider
from azure.identity.aio import AzureCliCredential
from mem0 import AsyncMemory


def retrieve_company_report(company_code: str, detailed: bool) -> str:
    if company_code != "CNTS":
        raise ValueError("Company code not found")
    if not detailed:
        return "CNTS is a company that specializes in technology."
    return (
        "CNTS is a company that specializes in technology. "
        "It had a revenue of $10 million in 2022. It has 100 employees."
    )


async def main() -> None:
    """Example of memory usage with local Mem0 OSS context provider."""
    print("=== Mem0 Context Provider Example ===")

    # Each record in Mem0 should be associated with agent_id or user_id or application_id or thread_id.
    # In this example, we associate Mem0 records with user_id.
    user_id = str(uuid.uuid4())

    # For Azure authentication, run `az login` command in terminal or replace AzureCliCredential with preferred
    # authentication option.
    # By default, local Mem0 authenticates to your OpenAI using the OPENAI_API_KEY environment variable.
    # See the Mem0 documentation for other LLM providers and authentication options.
    local_mem0_client = AsyncMemory()
    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="FriendlyAssistant",
            instructions="You are a friendly assistant.",
            tools=retrieve_company_report,
            context_providers=Mem0Provider(user_id=user_id, mem0_client=local_mem0_client),
        ) as agent,
    ):
        # First ask the agent to retrieve a company report with no previous context.
        # The agent will not be able to invoke the tool, since it doesn't know
        # the company code or the report format, so it should ask for clarification.
        query = "Please retrieve my company report"
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")

        # Now tell the agent the company code and the report format that you want to use
        # and it should be able to invoke the tool and return the report.
        query = "I always work with CNTS and I always want a detailed report format. Please remember and retrieve it."
        print(f"User: {query}")
        result = await agent.run(query)
        print(f"Agent: {result}\n")

        print("\nRequest within a new thread:")

        # Create a new thread for the agent.
        # The new thread has no context of the previous conversation.
        thread = agent.get_new_thread()

        # Since we have the mem0 component in the thread, the agent should be able to
        # retrieve the company report without asking for clarification, as it will
        # be able to remember the user preferences from Mem0 component.
        query = "Please retrieve my company report"
        print(f"User: {query}")
        result = await agent.run(query, thread=thread)
        print(f"Agent: {result}\n")


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: python/samples/getting_started/context_providers/mem0/mem0_threads.py
================================================
# Copyright (c) Microsoft. All rights reserved.

import asyncio
import uuid

from agent_framework.azure import AzureAIAgentClient
from agent_framework.mem0 import Mem0Provider
from azure.identity.aio import AzureCliCredential


def get_user_preferences(user_id: str) -> str:
    """Mock function to get user preferences."""
    preferences = {
        "user123": "Prefers concise responses and technical details",
        "user456": "Likes detailed explanations with examples",
    }
    return preferences.get(user_id, "No specific preferences found")


async def example_global_thread_scope() -> None:
    """Example 1: Global thread_id scope (memories shared across all operations)."""
    print("1. Global Thread Scope Example:")
    print("-" * 40)

    global_thread_id = str(uuid.uuid4())
    user_id = "user123"

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="GlobalMemoryAssistant",
            instructions="You are an assistant that remembers user preferences across conversations.",
            tools=get_user_preferences,
            context_providers=Mem0Provider(
                user_id=user_id,
                thread_id=global_thread_id,
                scope_to_per_operation_thread_id=False,  # Share memories across all threads
            ),
        ) as global_agent,
    ):
        # Store some preferences in the global scope
        query = "Remember that I prefer technical responses with code examples when discussing programming."
        print(f"User: {query}")
        result = await global_agent.run(query)
        print(f"Agent: {result}\n")

        # Create a new thread - but memories should still be accessible due to global scope
        new_thread = global_agent.get_new_thread()
        query = "What do you know about my preferences?"
        print(f"User (new thread): {query}")
        result = await global_agent.run(query, thread=new_thread)
        print(f"Agent: {result}\n")


async def example_per_operation_thread_scope() -> None:
    """Example 2: Per-operation thread scope (memories isolated per thread).

    Note: When scope_to_per_operation_thread_id=True, the provider is bound to a single thread
    throughout its lifetime. Use the same thread object for all operations with that provider.
    """
    print("2. Per-Operation Thread Scope Example:")
    print("-" * 40)

    user_id = "user123"

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="ScopedMemoryAssistant",
            instructions="You are an assistant with thread-scoped memory.",
            tools=get_user_preferences,
            context_providers=Mem0Provider(
                user_id=user_id,
                scope_to_per_operation_thread_id=True,  # Isolate memories per thread
            ),
        ) as scoped_agent,
    ):
        # Create a specific thread for this scoped provider
        dedicated_thread = scoped_agent.get_new_thread()

        # Store some information in the dedicated thread
        query = "Remember that for this conversation, I'm working on a Python project about data analysis."
        print(f"User (dedicated thread): {query}")
        result = await scoped_agent.run(query, thread=dedicated_thread)
        print(f"Agent: {result}\n")

        # Test memory retrieval in the same dedicated thread
        query = "What project am I working on?"
        print(f"User (same dedicated thread): {query}")
        result = await scoped_agent.run(query, thread=dedicated_thread)
        print(f"Agent: {result}\n")

        # Store more information in the same thread
        query = "Also remember that I prefer using pandas and matplotlib for this project."
        print(f"User (same dedicated thread): {query}")
        result = await scoped_agent.run(query, thread=dedicated_thread)
        print(f"Agent: {result}\n")

        # Test comprehensive memory retrieval
        query = "What do you know about my current project and preferences?"
        print(f"User (same dedicated thread): {query}")
        result = await scoped_agent.run(query, thread=dedicated_thread)
        print(f"Agent: {result}\n")


async def example_multiple_agents() -> None:
    """Example 3: Multiple agents with different thread configurations."""
    print("3. Multiple Agents with Different Thread Configurations:")
    print("-" * 40)

    agent_id_1 = "agent_personal"
    agent_id_2 = "agent_work"

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="PersonalAssistant",
            instructions="You are a personal assistant that helps with personal tasks.",
            context_providers=Mem0Provider(
                agent_id=agent_id_1,
            ),
        ) as personal_agent,
        AzureAIAgentClient(async_credential=credential).create_agent(
            name="WorkAssistant",
            instructions="You are a work assistant that helps with professional tasks.",
            context_providers=Mem0Provider(
                agent_id=agent_id_2,
            ),
        ) as work_agent,
    ):
        # Store personal information
        query = "Remember that I like to exercise at 6 AM and prefer outdoor activities."
        print(f"User to Personal Agent: {query}")
        result = await personal_agent.run(query)
        print(f"Personal Agent: {result}\n")

        # Store work information
        query = "Remember that I have team meetings every Tuesday at 2 PM."
        print(f"User to Work Agent: {query}")
        result = await work_agent.run(query)
        print(f"Work Agent: {result}\n")

        # Test memory isolation
        query = "What do you know about my schedule?"
        print(f"User to Personal Agent: {query}")
        result = await personal_agent.run(query)
        print(f"Personal Agent: {result}\n")

        print(f"User to Work Agent: {query}")
        result = await work_agent.run(query)
        print(f"Work Agent: {result}\n")


async def main() -> None:
    """Run all Mem0 thread management examples."""
    print("=== Mem0 Thread Management Example ===\n")

    await example_global_thread_scope()
    await example_per_operation_thread_scope()
    await example_multiple_agents()


if __name__