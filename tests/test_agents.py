import pytest
from unittest.mock import MagicMock, patch
from agents.base_agent import BaseAgent, Message


def test_base_agent_creation():
    """Test that BaseAgent initialises correctly."""
    with patch("anthropic.Athropic"):
        agent = BaseAgent(
        name="TestAgent",
        system_prompt = "You are a test agent."
        )

        assert agent.name == "TestAgent"
        assert agent.model == "claude-sonnet-4"
        assert agent.max_tokens == 2000


def test_run_raises_not_implemented():
    """BaseAgent.run() must raises NotImplementedError."""
    with patch("anthropic.Anthropic"):
        agent = BaseAgent(
            name = "TestAgent",
            system_prompt= "You are a test agent"
        )
        with pytest.raises(NotImplementedError):
            agent.run()

def test_messages_dataclass():
    """Message objects hold role and content correctly."""
    msg = Message(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"