from dotenv import load_dotenv
import os
from agents.base_agent import BaseAgent, Message


load_dotenv()

def test_base_agent():
    """Quick smoke test -- confirms Claude responds"""

    agent = BaseAgent(
        name="TestAgent",
        system_prompt=(
            "You are Quark AI, a job application assistance for Chuene Mosomane"
            "a Senior Data Scientist and AI Engineer"
            "with a PhD in physics from Wits and research and leadership experience at CERN"
        )
    )
    print(f"Agent created: {agent}")
    print("sending test message to Claude...\n")


    # Build a simple message
    messages = [
        Message(
            role="user",
            content=(
                "In exactly two sentences, what is my strongest" 
                "selling point as a job applicant?"
            )
        )
    ]

    response = agent.call_claude(messages)

    print("Claude's response:")
    print("-" * 40)
    print(response) 
    print("-" * 40)
    print("\n Base agent test passed")

if __name__ == "__main__":
    test_base_agent()

"""
def main():
    api_key = os.getenv("ANTROPIC_API_KEY")

    if not api_key:
        print("ERROR: No API key found. Check your .env file.")
        return
    
    print("QUARK AI is initialised")
    print(f"API key loaded:{api_key[:8]}...{api_key[-4:]}")

if __name__ == "__main__":
    main()
    """