from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from .prompt import PROMPT


def create_before_agent_callback():
    def before_agent_callback(callback_context: CallbackContext):
        user_query = callback_context.user_content.parts[0].text
        print(f"[{callback_context.agent_name}] User Query: {user_query}")

        # simple check for event keyword
        if 'event' not in user_query:
            return types.Content(role='guardrails', parts=[types.Part(text="Cannot help with that. Please specify an calendar related operation")])
        return None
    
    return before_agent_callback

def create_calendar_agent():
    before_agent_callback = create_before_agent_callback()
    
    agent = LlmAgent(
        name="chat_agent",
        model=LiteLlm("openai/gpt-4o-mini"),
        description="Simple agent to chat with the user",
        instruction=PROMPT,
        before_agent_callback=before_agent_callback
    )

    return agent