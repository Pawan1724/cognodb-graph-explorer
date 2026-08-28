import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("COGNODB_URI", "bolt://localhost:7687")
USER = os.getenv("COGNODB_USER", "neo4j")
PASSWORD = os.getenv("COGNODB_PASSWORD", "password")

# max_connection_lifetime keeps connections fresh so CognoDB doesn't kill idle ones
driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD),
    max_connection_lifetime=200,  # recycle connections every ~3 min
)

def get_session():
    return driver.session()
