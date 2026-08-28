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

def generate_cypher(question: str) -> str:
    if not client:
        return "MATCH (n) RETURN n LIMIT 5"  # Dummy fallback
    prompt = f"""
    {SCHEMA_CONTEXT}
    Convert the following natural language question into a read-only Cypher query (MATCH, RETURN, WHERE, etc.).
    IMPORTANT INSTRUCTION: ALWAYS RETURN THE FULL NODE ENTITIES AND THEIR RELATIONSHIPS (e.g., `RETURN p, r, proj` instead of just `RETURN p, proj` or string properties like `RETURN p.name`). If you do not return the relationship variable (like `r`), the frontend graph visualization will draw nodes without any connecting lines!
    Do not include any explanation or markdown formatting in your output, just the raw Cypher query.
    Only output the Cypher query, nothing else. No backticks, no code fences.
    Question: {question}
    Cypher Query:
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content.strip().replace("```cypher", "").replace("```", "").strip()

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
