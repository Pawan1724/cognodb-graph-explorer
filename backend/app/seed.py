"""
Populates CognoDB with a realistic, deterministic org/skills/projects graph.

Run with:  python -m app.seed
Safe to re-run: it clears prior data from this seed before reloading.
"""
import random

from faker import Faker

from .db import graph_db

fake = Faker()
Faker.seed(42)
random.seed(42)

DEPARTMENTS = ["Engineering", "Product", "Design", "Data"]
TEAMS = {
    "Engineering": ["Platform", "Infra", "Mobile"],
    "Product": ["Growth", "Core Product"],
    "Design": ["Product Design"],
    "Data": ["Analytics", "ML"],
}
SKILLS = [
    ("Python", "Language"), ("JavaScript", "Language"), ("Go", "Language"),
    ("Cypher", "Query Language"), ("SQL", "Query Language"),
    ("React", "Framework"), ("FastAPI", "Framework"), ("Kubernetes", "Infra"),
    ("AWS", "Infra"), ("Terraform", "Infra"), ("Figma", "Design Tool"),
    ("User Research", "Design Skill"), ("A/B Testing", "Product Skill"),
    ("Data Modeling", "Data Skill"), ("Machine Learning", "Data Skill"),
    ("System Design", "Engineering Skill"), ("Neo4j", "Query Language"),
]
CERTS = [
    ("AWS Certified Solutions Architect", "AWS"),
    ("Certified Kubernetes Administrator", "CNCF"),
    ("PMP", "PMI"),
]
PROJECTS = [
    ("Atlas Migration", "Active", "Migrate the monolith onto Kubernetes.", ["Kubernetes", "Terraform", "Go"]),
    ("Growth Experiments Q3", "Active", "A/B test onboarding flows.", ["A/B Testing", "React", "SQL"]),
    ("Insight Dashboard", "Active", "Internal analytics dashboard.", ["Python", "SQL", "Data Modeling"]),
    ("Recommendation Engine", "Active", "Graph-based recommendation service.", ["Python", "Neo4j", "Cypher", "Machine Learning"]),
    ("Design System 2.0", "Completed", "Rebuild the shared component library.", ["Figma", "React"]),
    ("Mobile Revamp", "Active", "Rewrite the mobile app.", ["React", "JavaScript", "System Design"]),
]
LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]
SENIORITY = ["Junior", "Mid", "Senior", "Staff", "Principal"]


def clear_seed_data():
    graph_db.run_write("MATCH (n) WHERE n.seed_batch = 'orgskill_v1' DETACH DELETE n")


def build_employees(n=45):
    employees = []
    for i in range(n):
        dept = random.choice(DEPARTMENTS)
        team = random.choice(TEAMS[dept])
        employees.append({
            "id": f"emp_{i:03d}",
            "name": fake.unique.name(),
            "title": random.choice(["Engineer", "Senior Engineer", "Manager", "Designer", "Analyst", "Data Scientist"]),
            "seniority": random.choice(SENIORITY),
            "hire_date": fake.date_between(start_date="-6y", end_date="-1m").isoformat(),
            "department": dept,
            "team": team,
        })
    return employees


def seed():
    print("Clearing previous seed data (if any)...")
    clear_seed_data()

    print("Creating departments and teams...")
    for dept in DEPARTMENTS:
        graph_db.run_write(
            "MERGE (d:Department {name: $name}) SET d.seed_batch = 'orgskill_v1'",
            {"name": dept},
        )
        for team in TEAMS[dept]:
            graph_db.run_write(
                """
                MATCH (d:Department {name: $dept})
                MERGE (t:Team {name: $team})
                SET t.seed_batch = 'orgskill_v1'
                MERGE (t)-[:PART_OF]->(d)
                """,
                {"dept": dept, "team": team},
            )

    print("Creating skills...")
    for name, category in SKILLS:
        graph_db.run_write(
            "MERGE (s:Skill {name: $name}) SET s.category = $category, s.seed_batch = 'orgskill_v1'",
            {"name": name, "category": category},
        )

    print("Creating certifications...")
    for name, issuer in CERTS:
        graph_db.run_write(
            "MERGE (c:Certification {name: $name}) SET c.issuer = $issuer, c.seed_batch = 'orgskill_v1'",
            {"name": name, "issuer": issuer},
        )

    print("Creating projects and their required skills...")
    for name, status, desc, req_skills in PROJECTS:
        graph_db.run_write(
            """
            MERGE (p:Project {name: $name})
            SET p.status = $status, p.description = $desc, p.start_date = $start, p.seed_batch = 'orgskill_v1'
            """,
            {"name": name, "status": status, "desc": desc, "start": fake.date_between(start_date="-1y", end_date="-1m").isoformat()},
        )
        for skill in req_skills:
            graph_db.run_write(
                """
                MATCH (p:Project {name: $name}), (s:Skill {name: $skill})
                MERGE (p)-[r:REQUIRES_SKILL]->(s)
                SET r.min_level = $level
                """,
                {"name": name, "skill": skill, "level": random.choice(LEVELS[1:])},
            )

    print("Creating employees...")
    employees = build_employees()
    for e in employees:
        graph_db.run_write(
            """
            MERGE (emp:Employee {id: $id})
            SET emp.name = $name, emp.title = $title, emp.seniority = $seniority,
                emp.hire_date = $hire_date, emp.seed_batch = 'orgskill_v1'
            WITH emp
            MATCH (t:Team {name: $team})
            MERGE (emp)-[:MEMBER_OF]->(t)
            """,
            e,
        )

    print("Building the reporting hierarchy...")
    # Within each team, the most senior person becomes the manager of the rest.
    by_team: dict[str, list[dict]] = {}
    for e in employees:
        by_team.setdefault(e["team"], []).append(e)

    for team, members in by_team.items():
        ranked = sorted(members, key=lambda m: SENIORITY.index(m["seniority"]), reverse=True)
        manager = ranked[0]
        for report in ranked[1:]:
            graph_db.run_write(
                """
                MATCH (report:Employee {id: $report_id}), (mgr:Employee {id: $mgr_id})
                MERGE (report)-[:REPORTS_TO]->(mgr)
                """,
                {"report_id": report["id"], "mgr_id": manager["id"]},
            )

    print("Assigning skills to employees...")
    skill_names = [s[0] for s in SKILLS]
    for e in employees:
        for skill in random.sample(skill_names, k=random.randint(2, 5)):
            graph_db.run_write(
                """
                MATCH (emp:Employee {id: $id}), (s:Skill {name: $skill})
                MERGE (emp)-[r:HAS_SKILL]->(s)
                SET r.level = $level, r.years = $years
                """,
                {
                    "id": e["id"],
                    "skill": skill,
                    "level": random.choice(LEVELS),
                    "years": random.randint(1, 8),
                },
            )

    print("Assigning employees to projects...")
    project_names = [p[0] for p in PROJECTS]
    for e in employees:
        for project in random.sample(project_names, k=random.randint(0, 2)):
            graph_db.run_write(
                """
                MATCH (emp:Employee {id: $id}), (p:Project {name: $project})
                MERGE (emp)-[r:WORKED_ON]->(p)
                SET r.role = $role
                """,
                {"id": e["id"], "project": project, "role": e["title"]},
            )

    print("Assigning a few certifications...")
    cert_names = [c[0] for c in CERTS]
    for e in random.sample(employees, k=15):
        graph_db.run_write(
            """
            MATCH (emp:Employee {id: $id}), (c:Certification {name: $cert})
            MERGE (emp)-[:HOLDS_CERT]->(c)
            """,
            {"id": e["id"], "cert": random.choice(cert_names)},
        )

    print("Adding a handful of mentorships...")
    for e in random.sample(employees, k=10):
        mentor = random.choice(employees)
        if mentor["id"] != e["id"]:
            graph_db.run_write(
                """
                MATCH (mentor:Employee {id: $mentor_id}), (mentee:Employee {id: $mentee_id})
                MERGE (mentor)-[:MENTORS]->(mentee)
                """,
                {"mentor_id": mentor["id"], "mentee_id": e["id"]},
            )

    print(f"Done. Seeded {len(employees)} employees across {len(DEPARTMENTS)} departments.")


if __name__ == "__main__":
    seed()
