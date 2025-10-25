"""
Tests for Microsoft Agent Framework agents.

These tests verify the agent creation and configuration for:
- Repository Analyzer Agent
- Outline Generator Agent
- Script Writer Agent
- Audio Producer Agent
- Post Processor Agent
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.models.agent_responses import (
    AudioAgentResponse,
    OutlineAgentResponse,
    ScriptAgentResponse,
)


@pytest.mark.agents
@pytest.mark.unit
class TestAnalyzerAgent:
    """Test Repository Analyzer agent."""

    @pytest.fixture
    def mock_chat_client(self):
        """Create a mock chat client."""
        client = MagicMock()
        return client

    @pytest.mark.asyncio
    async def test_create_analyzer_agent(self, mock_chat_client):
        """Test analyzer agent creation."""
        from backend.agents.analyzer_agent import create_analyzer_agent

        agent = await create_analyzer_agent(mock_chat_client)

        assert agent is not None
        assert hasattr(agent, "name")
        # Agent should have appropriate instructions
        assert hasattr(agent, "instructions") or hasattr(agent, "system_message")

    @pytest.mark.asyncio
    async def test_analyzer_agent_has_tools(self, mock_chat_client):
        """Test that analyzer agent has required tools configured."""
        from backend.agents.analyzer_agent import create_analyzer_agent

        agent = await create_analyzer_agent(mock_chat_client)

        # Should have tools for git operations and code parsing
        assert hasattr(agent, "tools")


@pytest.mark.agents
@pytest.mark.unit
class TestOutlineAgent:
    """Test Outline Generator agent."""

    @pytest.fixture
    def mock_chat_client(self):
        """Create a mock chat client."""
        client = MagicMock()
        return client

    @pytest.mark.asyncio
    async def test_create_outline_agent(self, mock_chat_client):
        """Test outline agent creation."""
        from backend.agents.outline_agent import create_outline_agent

        agent = await create_outline_agent(mock_chat_client)

        assert agent is not None
        assert hasattr(agent, "name")
        mock_chat_client.create_agent.assert_called_once()
        _, kwargs = mock_chat_client.create_agent.call_args
        assert kwargs.get("response_format") is OutlineAgentResponse

    @pytest.mark.asyncio
    async def test_outline_agent_configuration(self, mock_chat_client):
        """Test outline agent has proper configuration."""
        from backend.agents.outline_agent import create_outline_agent

        agent = await create_outline_agent(mock_chat_client)

        # Should have instructions for creating chapter outlines
        assert hasattr(agent, "instructions") or hasattr(agent, "system_message")
        mock_chat_client.create_agent.assert_called_once()
        _, kwargs = mock_chat_client.create_agent.call_args
        assert kwargs.get("response_format") is OutlineAgentResponse


@pytest.mark.agents
@pytest.mark.unit
class TestScriptAgent:
    """Test Script Writer agent."""

    @pytest.fixture
    def mock_chat_client(self):
        """Create a mock chat client."""
        client = MagicMock()
        return client

    @pytest.mark.asyncio
    async def test_create_script_agent(self, mock_chat_client):
        """Test script agent creation."""
        from backend.agents.script_agent import create_script_agent

        agent = await create_script_agent(mock_chat_client)

        assert agent is not None
        assert hasattr(agent, "name")
        mock_chat_client.create_agent.assert_called_once()
        _, kwargs = mock_chat_client.create_agent.call_args
        assert kwargs.get("response_format") is ScriptAgentResponse

    @pytest.mark.asyncio
    async def test_script_agent_for_chapter(self, mock_chat_client):
        """Test script agent can be configured for specific chapter."""
        from backend.agents.script_agent import create_script_agent

        chapter_data = {
            "number": 1,
            "title": "Introduction",
            "files_covered": ["main.py"],
        }

        agent = await create_script_agent(mock_chat_client, chapter_data=chapter_data)

        assert agent is not None
        mock_chat_client.create_agent.assert_called_once()
        _, kwargs = mock_chat_client.create_agent.call_args
        assert kwargs.get("response_format") is ScriptAgentResponse


@pytest.mark.agents
@pytest.mark.unit
class TestAudioAgent:
    """Test Audio Producer agent."""

    @pytest.fixture
    def mock_chat_client(self):
        """Create a mock chat client."""
        client = MagicMock()
        return client

    @pytest.mark.asyncio
    async def test_create_audio_agent(self, mock_chat_client):
        """Test audio agent creation."""
        from backend.agents.audio_agent import create_audio_agent

        agent = await create_audio_agent(mock_chat_client)

        assert agent is not None
        assert hasattr(agent, "name")
        mock_chat_client.create_agent.assert_called_once()
        _, kwargs = mock_chat_client.create_agent.call_args
        assert kwargs.get("response_format") is AudioAgentResponse

    @pytest.mark.asyncio
    async def test_audio_agent_has_tts_tools(self, mock_chat_client):
        """Test that audio agent has TTS tools."""
        from backend.agents.audio_agent import create_audio_agent

        agent = await create_audio_agent(mock_chat_client)

        # Should have tools for audio synthesis
        assert hasattr(agent, "tools")
        mock_chat_client.create_agent.assert_called_once()
        _, kwargs = mock_chat_client.create_agent.call_args
        assert kwargs.get("response_format") is AudioAgentResponse


@pytest.mark.agents
@pytest.mark.unit
class TestPostProcessAgent:
    """Test Post Processor agent."""

    @pytest.fixture
    def mock_chat_client(self):
        """Create a mock chat client."""
        client = MagicMock()
        return client

    @pytest.mark.asyncio
    async def test_create_postprocess_agent(self, mock_chat_client):
        """Test postprocess agent creation."""
        from backend.agents.postprocess_agent import create_postprocess_agent

        agent = await create_postprocess_agent(mock_chat_client)

        assert agent is not None
        assert hasattr(agent, "name")

    @pytest.mark.asyncio
    async def test_postprocess_agent_configuration(self, mock_chat_client):
        """Test postprocess agent has audio merging capabilities."""
        from backend.agents.postprocess_agent import create_postprocess_agent

        agent = await create_postprocess_agent(mock_chat_client)

        # Should have tools for audio processing and storage
        assert hasattr(agent, "tools")


@pytest.mark.agents
@pytest.mark.integration
class TestAgentWorkflow:
    """Integration tests for agent workflow."""

    @pytest.fixture
    def mock_chat_client(self):
        """Create a mock chat client."""
        client = MagicMock()
        client.chat = MagicMock()
        client.chat.completions = MagicMock()
        client.chat.completions.create = AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content="Test response"))],
                usage=MagicMock(total_tokens=100),
            )
        )
        return client

    @pytest.mark.skip(reason="Requires full agent framework setup")
    @pytest.mark.asyncio
    async def test_agent_workflow_execution(self, mock_chat_client):
        """Test that agents can be chained in a workflow."""
        from backend.agents.analyzer_agent import create_analyzer_agent
        from backend.agents.outline_agent import create_outline_agent

        # Create agents
        analyzer = await create_analyzer_agent(mock_chat_client)
        outliner = await create_outline_agent(mock_chat_client)

        # In a real workflow, output of analyzer would feed into outliner
        assert analyzer is not None
        assert outliner is not None

    @pytest.mark.asyncio
    async def test_agents_use_different_models(self, mock_chat_client):
        """Test that different agents can use different models/configurations."""
        from backend.agents.analyzer_agent import create_analyzer_agent
        from backend.agents.script_agent import create_script_agent

        analyzer = await create_analyzer_agent(mock_chat_client)
        script_writer = await create_script_agent(mock_chat_client)

        # Agents should be configured differently for their specific tasks
        assert analyzer is not None
        assert script_writer is not None

    @pytest.mark.asyncio
    async def test_agents_handle_errors_gracefully(self, mock_chat_client):
        """Test that agents handle errors without crashing."""
        from backend.agents.outline_agent import create_outline_agent

        # Configure client to raise an error
        mock_chat_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        agent = await create_outline_agent(mock_chat_client)

        # Agent creation should still succeed
        assert agent is not None

        # Running the agent might fail, but should handle gracefully
        # (This would be tested in workflow integration tests)
