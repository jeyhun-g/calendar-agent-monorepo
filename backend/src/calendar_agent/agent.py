from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

agent = LlmAgent(
    name="chat_agent",
    model=LiteLlm("openai/gpt-4o-mini"),
    description="Simple agent to chat with the user",
    instruction="I can answer your questions and chat with you"
)