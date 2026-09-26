from ai_data_agent.llm.provider import get_chat_model

model = get_chat_model()
response = model.invoke("Reply with exactly one word: hello")
print(response.content)