// 10 Example queries that the application should support
// Parameters (e.g. $person_name) are used to prevent injection and improve performance.

// 1. What projects is Rahul working on? (1-hop)
MATCH (p:Person {name: 'Rahul'})-[:WORKS_ON]->(proj:Project)
RETURN proj.name, proj.status;

// 2. What tasks are pending for the Apollo project? (2-hop)
MATCH (t:Task {status: 'Pending'})-[:BELONGS_TO]->(proj:Project {name: 'Apollo'})
RETURN t.title, t.priority, t.due_date;

// 3. Who attended meetings related to the Apollo project? (2-hop)
MATCH (p:Person)-[:ATTENDED]->(m:Meeting)-[:RELATED_TO]->(proj:Project {name: 'Apollo'})
RETURN DISTINCT p.name, p.role, m.title;

// 4. Which people are connected to the Apollo project? (Multi-hop)
// Demonstrates graph value by finding indirect connections (up to 2 hops away)
MATCH (p:Person)-[*1..2]-(proj:Project {name: 'Apollo'})
RETURN DISTINCT p.name, p.role;

// 5. What emails are related to the Apollo project? (1-hop)
MATCH (e:Email)-[:RELATED_TO]->(proj:Project {name: 'Apollo'})
RETURN e.subject, e.timestamp;

// 6. Which projects does Pawan work on? (1-hop)
MATCH (p:Person {name: 'Pawan'})-[:WORKS_ON]->(proj:Project)
RETURN proj.name, proj.description;

// 7. What tasks are overdue across all projects? (Filtering & 1-hop)
MATCH (t:Task)
WHERE t.status <> 'Completed' AND t.due_date < '2026-08-27'
MATCH (t)-[:BELONGS_TO]->(proj:Project)
RETURN t.title, t.due_date, proj.name;

// 8. Which people are working on the same projects as Rahul? (Multi-hop Collaborative Filtering)
MATCH (p1:Person {name: 'Rahul'})-[:WORKS_ON]->(proj:Project)<-[:WORKS_ON]-(p2:Person)
RETURN DISTINCT p2.name, proj.name;

// 9. What happened in the latest Apollo meeting? (2-hop with ordering)
MATCH (m:Meeting)-[:RELATED_TO]->(proj:Project {name: 'Apollo'})
RETURN m.title, m.date, m.summary
ORDER BY m.date DESC LIMIT 1;

// 10. Which companies own projects that Rahul is working on? (2-hop)
MATCH (p:Person {name: 'Rahul'})-[:WORKS_ON]->(proj:Project)<-[:OWNS]-(c:Company)
RETURN DISTINCT c.name, proj.name;
