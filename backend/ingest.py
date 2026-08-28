import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("COGNODB_URI")
USER = os.getenv("COGNODB_USER")
PASSWORD = os.getenv("COGNODB_PASSWORD")

if not URI or not PASSWORD:
    raise ValueError("Missing database credentials in .env")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), "r") as f:
        return json.load(f)

def ingest_data():
    with driver.session() as session:
        # Clear existing data for a fresh start (optional, but good for take-home)
        print("Clearing existing graph...")
        session.run("MATCH (n) DETACH DELETE n")

        # 1. Companies
        companies = load_json("companies.json")
        for c in companies:
            session.run("""
                MERGE (comp:Company {id: $id})
                SET comp.name = $name, comp.industry = $industry
            """, **c)
        print(f"Loaded {len(companies)} companies.")

        # 2. People and WORKS_AT
        people = load_json("people.json")
        for p in people:
            session.run("""
                MERGE (person:Person {id: $id})
                SET person.name = $name, person.email = $email, person.role = $role, person.department = $department
                WITH person
                MATCH (comp:Company {id: $works_at})
                MERGE (person)-[:WORKS_AT]->(comp)
            """, **p)
        print(f"Loaded {len(people)} people.")

        # 3. Projects, OWNS, and WORKS_ON
        projects = load_json("projects.json")
        for p in projects:
            session.run("""
                MERGE (proj:Project {id: $id})
                SET proj.name = $name, proj.description = $description, proj.status = $status, proj.start_date = $start_date
                WITH proj
                MATCH (comp:Company {id: $owned_by})
                MERGE (comp)-[:OWNS]->(proj)
            """, **p)
            for w in p.get("workers", []):
                session.run("""
                    MATCH (proj:Project {id: $proj_id})
                    MATCH (person:Person {id: $person_id})
                    MERGE (person)-[r:WORKS_ON]->(proj)
                    SET r.role = $role
                """, proj_id=p["id"], person_id=w["id"], role=w["role"])
        print(f"Loaded {len(projects)} projects.")

        # 4. Tasks, BELONGS_TO, and ASSIGNED_TO
        tasks = load_json("tasks.json")
        for t in tasks:
            session.run("""
                MERGE (task:Task {id: $id})
                SET task.title = $title, task.description = $description, task.status = $status, task.priority = $priority, task.due_date = $due_date
                WITH task
                MATCH (proj:Project {id: $belongs_to})
                MERGE (task)-[:BELONGS_TO]->(proj)
                WITH task
                MATCH (person:Person {id: $assigned_to})
                MERGE (person)-[r:ASSIGNED_TO]->(task)
                SET r.assigned_date = $assigned_date
            """, **t)
        print(f"Loaded {len(tasks)} tasks.")

        # 5. Meetings, RELATED_TO, and ATTENDED
        meetings = load_json("meetings.json")
        for m in meetings:
            session.run("""
                MERGE (meeting:Meeting {id: $id})
                SET meeting.title = $title, meeting.date = $date, meeting.summary = $summary
                WITH meeting
                MATCH (proj:Project {id: $related_to})
                MERGE (meeting)-[:RELATED_TO]->(proj)
            """, **m)
            for attendee_id in m.get("attendees", []):
                session.run("""
                    MATCH (meeting:Meeting {id: $meeting_id})
                    MATCH (person:Person {id: $person_id})
                    MERGE (person)-[:ATTENDED]->(meeting)
                """, meeting_id=m["id"], person_id=attendee_id)
        print(f"Loaded {len(meetings)} meetings.")

        # 6. Emails, RELATED_TO, SENT, and RECEIVED
        emails = load_json("emails.json")
        for e in emails:
            session.run("""
                MERGE (email:Email {id: $id})
                SET email.subject = $subject, email.body = $body, email.timestamp = $timestamp
                WITH email
                MATCH (proj:Project {id: $related_to})
                MERGE (email)-[:RELATED_TO]->(proj)
                WITH email
                MATCH (sender:Person {id: $sender})
                MERGE (sender)-[:SENT]->(email)
            """, **e)
            for receiver_id in e.get("receivers", []):
                session.run("""
                    MATCH (email:Email {id: $email_id})
                    MATCH (receiver:Person {id: $receiver_id})
                    MERGE (receiver)-[:RECEIVED]->(email)
                """, email_id=e["id"], receiver_id=receiver_id)
        print(f"Loaded {len(emails)} emails.")

    driver.close()

if __name__ == "__main__":
    ingest_data()
    print("Ingestion complete!")
