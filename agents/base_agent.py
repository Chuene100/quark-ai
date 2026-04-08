import os
import anthropic
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    """Represents a sing message in a conversation"""
    role: str
    content: str

@dataclass
class BaseAgent:
    """The foundation for all Quark AI agents. Every specialist agent inherits from this class"""
    name: str
    system_prompt: str
    model: str = "claude-sonnet"
    max_tokens: int = 2000
    temperature: float = 0.5

    def __post_init__(self):
        """Called automatically after __init__. Sets up the Anthropic client using API key from .env"""
        self.client = anthropic.Anthropic(
            api_key=os.getenv("")
        )

    def call_claude(
            self,
            messages: list[Message],
            max_tokens: Optional[int] = None,
            temperature: Optional[float] = None,
    ) -> str:
        """Sends a conversation to Claude and returns the reponse text.
        Args:
            message: list of Message objects ( the conversation so far)
            max_tokens: override dafault if needed
            temperature: override default if needed (0=focused, 1=creative)

        Returns:
            Claude's response as a plain string
        """
        # Convert our Message dataclasses to the dict format Claude expects
        formatted = [
            {"role": m.role, "content": m.comtent}
            for m in messages
        ]

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                system=self.system_prompt,
                messages=formatted,
            )
            return response.content[0].text
        
        except anthropic.AuthenticationError:
            raise ValueError(
                "Invalid API key. Check your .env file"
            )
        except anthropic.RateLimitError:
            raise ValueError(
                "Rate limit hit. Wait a moment and try again."
            )
        except anthropic.APIError as e:
            raise ValueError(f"Claude API error: {str(e)}")
        
    def run(self, **kwargs) -> dict:
        """
        Every subclass must implement its own run() method.
        This enforces the pattern -- If you forget, Python reminds you.
        """
        raise NotImplementedError(
            f"Agent'{self.name}' must implemtn a run() method"
        )
    
    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}', model='self.model'>"