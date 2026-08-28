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
  (:Employee {id: string, name: string, title: string, seniority: string, hire_date: string})
  (:Department {name: string})
  (:Team {name: string})
  (:Skill {name: string, category: string})
  (:Project {name: string, status: string, start_date: string, description: string})
  (:Certification {name: string, issuer: string})

Relationship types:
  (:Employee)-[:REPORTS_TO]->(:Employee)                 -- e reports to their manager
  (:Employee)-[:MEMBER_OF]->(:Team)
  (:Team)-[:PART_OF]->(:Department)
  (:Employee)-[:HAS_SKILL {level: string, years: integer}]->(:Skill)   -- level is one of Beginner, Intermediate, Advanced, Expert
  (:Project)-[:REQUIRES_SKILL {min_level: string}]->(:Skill)
  (:Employee)-[:WORKED_ON {role: string, start_date: string, end_date: string}]->(:Project)
  (:Employee)-[:HOLDS_CERT]->(:Certification)
  (:Employee)-[:MENTORS]->(:Employee)

Notes:
  - REPORTS_TO points from a report up to their manager, so a variable-length
    path REPORTS_TO*1..5 from an employee walks up the org chart.
  - Only MATCH / OPTIONAL MATCH / WHERE / RETURN / ORDER BY / LIMIT are
    permitted. Never generate CREATE, MERGE, DELETE, SET, or REMOVE.
"""

SAMPLE_QUERIES = {
    "org_chain": {
        "label": "Who does this person ultimately report to?",
        "cypher": """
            MATCH path = (e:Employee {name: $name})-[:REPORTS_TO*1..6]->(top:Employee)
            RETURN [n IN nodes(path) | n.name] AS chain
            ORDER BY length(path) DESC
            LIMIT 1
        """,
        "default_params": {"name": "Aarav Sharma"},
    },
    "project_staffing_candidates": {
        "label": "Who could staff this project but isn't on it yet?",
        "cypher": """
            MATCH (p:Project {name: $project})-[:REQUIRES_SKILL]->(s:Skill)
            MATCH (e:Employee)-[hs:HAS_SKILL]->(s)
            WHERE NOT (e)-[:WORKED_ON]->(p)
            WITH e, count(DISTINCT s) AS matched_skills
            MATCH (p2:Project {name: $project})-[:REQUIRES_SKILL]->(allSkills:Skill)
            WITH e, matched_skills, count(DISTINCT allSkills) AS total_skills
            WHERE matched_skills = total_skills
            RETURN e.name AS candidate, e.title AS title, matched_skills
            ORDER BY candidate
        """,
        "default_params": {"project": "Atlas Migration"},
    },
    "shortest_org_path": {
        "label": "Shortest org-chart connection between two people",
        "cypher": """
            MATCH (a:Employee {name: $name_a}), (b:Employee {name: $name_b})
            MATCH path = shortestPath((a)-[:REPORTS_TO*..8]-(b))
            RETURN [n IN nodes(path) | n.name] AS chain, length(path) AS hops
        """,
        "default_params": {"name_a": "Aarav Sharma", "name_b": "Diya Nair"},
    },
    "skill_gap": {
        "label": "Skills required by active projects that nobody in a department has",
        "cypher": """
            MATCH (dept:Department {name: $department})<-[:PART_OF]-(:Team)<-[:MEMBER_OF]-(e:Employee)
            WITH dept, collect(DISTINCT e) AS deptEmployees
            MATCH (p:Project {status: "Active"})-[:REQUIRES_SKILL]->(s:Skill)
            WHERE NOT EXISTS {
                MATCH (any:Employee)-[:HAS_SKILL]->(s)
                WHERE any IN deptEmployees
            }
            RETURN DISTINCT s.name AS missing_skill, p.name AS needed_for_project
            ORDER BY missing_skill
        """,
        "default_params": {"department": "Engineering"},
    },
}
