# CognoDB Graph Explorer

**CognoDB Graph Explorer** is an AI-powered natural-language interface and visual exploration tool for graph databases. Built seamlessly on top of CognoDB (Neo4j) and the DeepSeek AI model, it allows users to instantly translate complex English questions into native Cypher queries, executing them securely and rendering the resulting multi-hop relationships in an interactive, layered graph visualization.

## Live Demo

**Application:** https://graphdatabasewexaai.netlify.app/

## Demo Video

[CognoDB Graph Explorer Demo](https://drive.google.com/file/d/1wXLPwiV57gu7fo6MiPzEGO4_Qudic9kf/view?usp=sharing)

## Problem

Workplace information is fundamentally interconnected: people work on projects, attend meetings, send emails, and complete tasks. However, this data is normally siloed across disparate systems such as HR databases, JIRA, and Outlook. Answering holistic questions about how a company operates is difficult when data is scattered across rigid, tabular schemas.

## Solution

This application unifies these entities into a single workplace knowledge graph. Users can ask natural language questions (e.g., *"Who attended meetings about projects owned by Stark Industries?"*), and the system dynamically translates this intent into a graph query, returning both structured answers and interactive node-link visualizations.

## Why a Graph Database?

Graph databases (like CognoDB / Neo4j) excel at answering questions about relationships. Consider the question: *"Which people are indirectly connected to the Apollo project through meetings or tasks?"*

In a relational database, this would require querying multiple tables (`People`, `Meetings`, `Meeting_Attendees`, `Tasks`, `Task_Assignees`, `Projects`) and performing expensive SQL `JOIN`s to stitch the paths together.

In a graph database, relationships are native, first-class citizens. The query simply traverses the connected paths:
`Person -> ATTENDED -> Meeting -> RELATED_TO -> Project`
and
`Person -> ASSIGNED_TO -> Task -> BELONGS_TO -> Project`
This multi-hop traversal is highly performant and intuitive to express in Cypher.

## Key Features

- Natural language graph querying
- NL → Cypher translation via LLM
- Cypher query validation and safety checking
- CognoDB integration via Bolt protocol
- Multi-hop relationship traversal
- Interactive, layered graph visualization

## Architecture

```mermaid
graph LR
    User[User / Browser] <-->|HTTP / JSON| FastAPI[FastAPI Backend]
    FastAPI <-->|Bolt Protocol| CognoDB[(CognoDB / Neo4j)]
    FastAPI <-->|Prompt / API| LLM[DeepSeek API]
  
    subgraph FastAPI Backend
        Router(API Routes)
        LLMService(NL to Cypher)
        Validator(Cypher Validator)
        DBService(Graph DB Driver)
      
        Router --> LLMService
        LLMService --> Validator
        Validator --> DBService
    end
```

## Graph Data Model

The schema represents typical workplace relationships.

```mermaid
graph TD
    Person((Person))
    Company((Company))
    Project((Project))
    Task((Task))
    Meeting((Meeting))
    Email((Email))

    Person -->|WORKS_AT| Company
    Person -->|WORKS_ON| Project
    Person -->|ASSIGNED_TO| Task
    Person -->|ATTENDED| Meeting
    Person -->|SENT / RECEIVED| Email
    Task -->|BELONGS_TO| Project
    Meeting -->|RELATED_TO| Project
    Email -->|RELATED_TO| Project
    Company -->|OWNS| Project
```

## Example Queries

### Multi-hop Query

**Question**: *"Which people are indirectly connected to the Apollo project through meetings or tasks?"*

**Generated Cypher**:

```cypher
MATCH (p:Person)-[:ATTENDED]->(m:Meeting)-[:RELATED_TO]->(proj:Project {name: "Apollo"})
RETURN p, m, proj
UNION
MATCH (p:Person)-[:ASSIGNED_TO]->(t:Task)-[:BELONGS_TO]->(proj:Project {name: "Apollo"})
RETURN p, t, proj
```

*Explanation*: This query uses `UNION` to traverse two distinct multi-hop paths to find all individuals connected to the Apollo project, demonstrating the flexibility of graph traversal over rigid tabular queries.

## Project Structure

```text
backend/
  app/
    main.py         # FastAPI application and routes
    llm.py          # LLM integration (NL2Cypher)
    db.py           # Neo4j database driver setup
    validators.py   # Cypher query security validation
    queries.py      # Core execution logic
  tests/            # Test suite
  ingest.py         # Seed data loader script
frontend/
  src/
    components/     # React UI components (GraphView, etc.)
    api.js          # Backend communication
cypher/
  schema.cypher     # Database constraints
data/
  *.json            # Raw seed data
docs/
  screenshots/      # UI screenshots
```

## Tech Stack

- **Database**: CognoDB (Neo4j compatible)
- **Backend**: Python, FastAPI, Official Neo4j Python Driver
- **Frontend**: React, Vite
- **AI**: DeepSeek API

## Setup

*(Follow the steps below to run locally)*

### CognoDB Setup

1. Create a free account at `console.cognodb.com`.
2. Create a free (c0) instance.
3. Save your connection URI (`bolt+s://<instance-id>.databases.cognodb.cloud`) and generated password.

### Environment Variables

Ensure `.env` files are created in the project (they are ignored by Git for security).
See `.env.example` in the repository root for the required variables:

```env
COGNODB_URI=bolt+s://<instance-id>.databases.cognodb.cloud
COGNODB_USER=cognodb
COGNODB_PASSWORD=your_password
DEEPSEEK_API_KEY=your_deepseek_key
```

### Seed Data

Data loading uses parameterized Cypher queries to safely ingest JSON into the graph.

```bash
cd backend
pip install -r requirements.txt
python ingest.py
```

*This creates the initial nodes (People, Projects, etc.) and connects them via relationships.*

### Running Locally

**Backend**:

```bash
cd backend
uvicorn app.main:app --reload
```

**Frontend**:

```bash
cd frontend
npm install
npm run dev
```

## Cypher Queries

The application supports executing dynamic Cypher generated by the LLM. Core query patterns include:

- **Direct relationship**: `MATCH (p:Person)-[:WORKS_ON]->(proj:Project) RETURN p, proj`
- **Multi-hop traversal**: `MATCH (p:Person)-[:ATTENDED]->(m:Meeting)-[:RELATED_TO]->(proj:Project) RETURN p, m, proj`
- **Relational-awkward discovery**: Traversing multiple disparate paths (Meetings OR Tasks) to discover project contributors without complex SQL unions/joins.

## Security

- **Environment Variables**: No secrets are hardcoded or committed to version control.
- **Cypher Validation**: A strict regex validator rejects dangerous operations (`CREATE`, `DELETE`, `DROP`, `MERGE`, etc.) before they reach the database.
- **Read-Only Execution**: It is recommended to use a read-only CognoDB user for runtime queries.
- **Parameterized Queries**: Where applicable, application logic and ingestion scripts utilize official Neo4j driver parameterization to prevent injection.

## Error Handling

The application handles failures gracefully:

- **Database Unreachable**: Returns a clean "Unable to connect to the graph database" message rather than a 500 stack trace.
- **No Results**: Displays an empty state ("No matching relationships were found") if the Cypher query returns 0 rows.
- **Invalid Cypher**: Safely catches Neo4j syntax errors and informs the user.

## Screenshots

*(Add real screenshots before final submission)*

- **Main Dashboard**
                       ![1787941466042](image/README/1787941466042.png)

- **Natural Language Query**
                        ![1787941573425](image/README/1787941573425.png)

- **Graph Visualization (Multi-hop)**
                       ![1787939791950](image/README/1787939791950.png)

## Testing

A test suite validates the security layer and API health.

```bash
cd backend
pytest tests/test_api.py
```

## Benchmark

Tested manually on a representative suite of 5 diverse queries.

- **Execution Accuracy**: 100% (Valid Cypher generated for all test cases).
- **Latency**: ~5 seconds end-to-end (Including LLM generation + Database execution + Synthesis).

## Limitations

- Highly complex queries may cause LLM hallucinations (generating invalid Cypher properties).
- The graph visualization is optimized for focused subgraphs; retrieving hundreds of nodes may cause visual clutter.

## Future Improvements

- Implement few-shot prompting or fine-tuning to improve NL2Cypher accuracy.
- Add user authentication and role-based access control.

## Author

Salikanti Pawan Kumar
