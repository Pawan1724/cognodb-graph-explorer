import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Setup DeepSeek API
api_key = os.getenv("DEEPSEEK_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
else:
    client = None

SCHEMA_CONTEXT = """
Graph Schema for WorkGraph AI:
Nodes:
- Person(id, name, email, role, department)
- Company(id, name, industry)
- Project(id, name, description, status, start_date)
- Task(id, title, description, status, priority, due_date)
- Meeting(id, title, date, summary)
- Email(id, subject, body, timestamp)

Relationships:
- (Person)-[:WORKS_AT]->(Company)
- (Person)-[:WORKS_ON {role}]->(Project)
- (Person)-[:ASSIGNED_TO {assigned_date}]->(Task)
- (Person)-[:ATTENDED]->(Meeting)
- (Person)-[:SENT]->(Email)
- (Person)-[:RECEIVED]->(Email)
- (Task)-[:BELONGS_TO]->(Project)
- (Meeting)-[:RELATED_TO]->(Project)
- (Email)-[:RELATED_TO]->(Project)
- (Company)-[:OWNS]->(Project)

Sample People in DB: Rahul Sharma, Pawan Kumar, Priya Nair, Arjun Reddy, Sneha Gupta,
Vikram Singh, Ananya Iyer, Karthik Menon, Diya Patel, Rohan Joshi, Meera Desai, Aditya Banerjee

Sample Projects: Apollo, Titan, CloudBridge, PaySecure, Chakra

Sample Companies: Stark Industries, Dravid Technologies, NexGen Solutions
"""

import json

def generate_cypher(question: str) -> dict:
    if not client:
        return {"query": "MATCH (n) RETURN n LIMIT 5", "parameters": {}}
    prompt = f"""
    {SCHEMA_CONTEXT}
    Convert the following natural language question into a read-only Cypher query.
    IMPORTANT INSTRUCTIONS:
    1. You MUST parameterize the query to prevent injection. Replace any literal values (names, titles, etc.) with parameters (e.g., $person_name).
    2. ALWAYS RETURN THE RELATIONSHIP VARIABLES along with the nodes. For example, use `MATCH (p:Person)-[r:WORKS_AT]->(c:Company) RETURN p, r, c`. If you omit the relationship variable `r` in the RETURN statement, the frontend graph will draw the nodes as disconnected dots!
    3. You must respond with a raw JSON object containing EXACTLY two keys: "query" (the Cypher string) and "parameters" (a dictionary of the parameters used).
    Do NOT wrap the output in markdown blocks. Output valid JSON only.
    
    Question: {question}
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    raw_response = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(raw_response)
        return parsed
    except json.JSONDecodeError:
        # Fallback if LLM fails to output valid JSON
        raise ValueError(f"LLM failed to return valid JSON. Raw output: {raw_response}")

def generate_answer(question: str, graph_data: list) -> str:
    if not client:
        return "This is a placeholder answer based on graph data."
    prompt = f"""
    Question: {question}
    Graph DB Result: {graph_data}
    Provide a clear, concise natural-language answer to the question based on the provided Graph DB Result.
    Be specific and mention names and details from the data.
    Answer:
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()
