import uuid

from ai_data_agent.agents.state import AgentState
from ai_data_agent.llm.provider import get_chat_model
from ai_data_agent.agents.judge import JUDGE_PROMPT_TEMPLATE

model = get_chat_model()

prompt = JUDGE_PROMPT_TEMPLATE.format(
    question="How many rides were completed?",
    sql="SELECT COUNT(*) FROM rides WHERE status = 'completed' LIMIT 500",
    result=[{"count": 3}],
    explanation="There are 3 completed rides.",
)

response = model.invoke(prompt)
print("--- RAW MODEL OUTPUT (repr, shows exact characters) ---")
print(repr(response.content))
