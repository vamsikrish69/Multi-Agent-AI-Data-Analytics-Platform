import uuid

from ai_data_agent.agents.etl_analyst import review_etl_code
from ai_data_agent.agents.state import AgentState

buggy_code = """
def load_rides(df):
    df['fare_amount'] = df['fare_amount'].astype(int)
    df['distance_km'] = df['distance_km'] / 0
    return df.to_sql('rides', con=engine, if_exists='replace')
"""

state = AgentState(
    user_question="Review this ETL function",
    correlation_id=str(uuid.uuid4()),
    code_to_review=buggy_code,
)
result = review_etl_code(state)
print(result.etl_review_notes)
