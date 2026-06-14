from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

from app.agent.dependencies import Deps
from app.agent.prompts import SYSTEM_PROMPT

model = GroqModel("llama-3.3-70b-versatile")

agent: Agent[Deps] = Agent(
    model,
    system_prompt=SYSTEM_PROMPT,
    deps_type=Deps,
)
