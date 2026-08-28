// Node labels and their properties:
//   (:Person {id: string, name: string, email: string, role: string, department: string})
//   (:Company {id: string, name: string, industry: string})
//   (:Project {id: string, name: string, description: string, status: string, start_date: string})
//   (:Task {id: string, title: string, description: string, status: string, priority: string, due_date: string})
//   (:Meeting {id: string, title: string, date: string, summary: string})
//   (:Email {id: string, subject: string, body: string, timestamp: string})

// 1. Direct relationship: Person -> Project
MATCH (p:Person {name: $person_name})-[:WORKS_ON]->(proj:Project)
RETURN p, proj

// 2. Person -> Meeting -> Project
MATCH (p:Person)-[:ATTENDED]->(m:Meeting)-[:RELATED_TO]->(proj:Project {name: $project_name})
RETURN p, m, proj

// 3. Multi-path traversal: Person connected to Project via Meeting OR Task
MATCH (p:Person)-[*1..2]-(proj:Project {name: $project_name})
RETURN DISTINCT p.name, p.role
