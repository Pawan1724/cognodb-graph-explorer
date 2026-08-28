"""
Two things live here:
1. SCHEMA_DESCRIPTION - a plain-text description of the graph, given to the
   LLM so it can translate natural language into valid Cypher for *this*
   schema rather than guessing.
2. SAMPLE_QUERIES - a handful of hand-written, parameterised Cypher queries
   that exercise the graph (multi-hop traversal, path-finding) and back the
   "Try an example" buttons in the UI. These also double as a sanity check
   that the schema and driver setup work independently of the LLM.
"""

SCHEMA_DESCRIPTION = """
Node labels and their properties:
  (:Person {id: string, name: string, email: string, role: string, department: string})
  (:Company {id: string, name: string, industry: string})
  (:Project {id: string, name: string, description: string, status: string, start_date: string})
  (:Task {id: string, title: string, description: string, status: string, priority: string, due_date: string})
  (:Meeting {id: string, title: string, date: string, summary: string})
  (:Email {id: string, subject: string, body: string, timestamp: string})

Relationship types:
  (:Person)-[:WORKS_AT]->(:Company)
  (:Person)-[:WORKS_ON {role: string}]->(:Project)
  (:Person)-[:ASSIGNED_TO {assigned_date: string}]->(:Task)
  (:Person)-[:ATTENDED]->(:Meeting)
  (:Person)-[:SENT]->(:Email)
  (:Person)-[:RECEIVED]->(:Email)
  (:Task)-[:BELONGS_TO]->(:Project)
  (:Meeting)-[:RELATED_TO]->(:Project)
  (:Email)-[:RELATED_TO]->(:Project)
  (:Company)-[:OWNS]->(:Project)

Notes:
  - Only MATCH / OPTIONAL MATCH / WHERE / RETURN / ORDER BY / LIMIT are permitted.
  - Never generate CREATE, MERGE, DELETE, SET, or REMOVE.
"""

SAMPLE_QUERIES = {
    "org_chain": {
        "label": "Which people attended meetings related to the Apollo project?",
        "cypher": """
            MATCH (p:Person)-[:ATTENDED]->(m:Meeting)-[:RELATED_TO]->(proj:Project {name: $project_name})
            RETURN DISTINCT p.name, p.role, m.title
        """,
        "default_params": {"project_name": "Apollo"},
    },
    "project_staffing_candidates": {
        "label": "What tasks are pending for the Apollo project?",
        "cypher": """
            MATCH (t:Task {status: 'Pending'})-[:BELONGS_TO]->(proj:Project {name: $project_name})
            RETURN t.title, t.priority, t.due_date
        """,
        "default_params": {"project_name": "Apollo"},
    },
    "shortest_org_path": {
        "label": "Show me everyone connected to the Apollo project through either meetings or tasks.",
        "cypher": """
            MATCH (p:Person)-[*1..2]-(proj:Project {name: $project_name})
            RETURN DISTINCT p.name, p.role
        """,
        "default_params": {"project_name": "Apollo"},
    },
    "skill_gap": {
        "label": "Show me the companies that own projects with a status of In Progress.",
        "cypher": """
            MATCH (c:Company)-[:OWNS]->(proj:Project {status: $project_status})
            RETURN DISTINCT c.name, proj.name
        """,
        "default_params": {"project_status": "In Progress"},
    },
}
