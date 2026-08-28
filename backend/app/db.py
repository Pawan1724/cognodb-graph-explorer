"""
Thin wrapper around the official Neo4j Python driver, pointed at CognoDB.
CognoDB speaks openCypher over Bolt, so the stock driver works unmodified -
only the URI, user and password differ from a self-hosted Neo4j instance.
"""
from contextlib import contextmanager
from typing import Any

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from neo4j.graph import Node, Relationship, Path

from .config import settings


def _extract_graph(value, nodes: dict, links: list):
    """Walk a Cypher result value and pull out any Node/Relationship/Path
    objects it contains, so the frontend can render them as a mini graph.
    Nodes are keyed by element id to dedupe across rows.
    """
    if isinstance(value, Node):
        nodes[value.element_id] = {
            "id": value.element_id,
            "labels": list(value.labels),
            "properties": dict(value.items()),
        }
    elif isinstance(value, Relationship):
        links.append(
            {
                "source": value.start_node.element_id,
                "target": value.end_node.element_id,
                "type": value.type,
                "properties": dict(value.items()),
            }
        )
        _extract_graph(value.start_node, nodes, links)
        _extract_graph(value.end_node, nodes, links)
    elif isinstance(value, Path):
        for node in value.nodes:
            _extract_graph(node, nodes, links)
        for rel in value.relationships:
            _extract_graph(rel, nodes, links)
    elif isinstance(value, list):
        for item in value:
            _extract_graph(item, nodes, links)
    elif isinstance(value, dict):
        for item in value.values():
            _extract_graph(item, nodes, links)


class DatabaseUnavailableError(Exception):
    """Raised when CognoDB can't be reached or credentials are rejected."""


class GraphDB:
    def __init__(self):
        self._driver = None

    def connect(self):
        if not settings.cognodb_uri or not settings.cognodb_password:
            raise DatabaseUnavailableError(
                "CognoDB connection details are missing. Set COGNODB_URI and "
                "COGNODB_PASSWORD in your environment."
            )
        self._driver = GraphDatabase.driver(
            settings.cognodb_uri,
            auth=(settings.cognodb_user, settings.cognodb_password),
        )

    def close(self):
        if self._driver:
            self._driver.close()

    def verify_connectivity(self) -> tuple[bool, str]:
        try:
            if self._driver is None:
                self.connect()
            self._driver.verify_connectivity()
            return True, "connected"
        except AuthError:
            return False, "Authentication with CognoDB failed. Check COGNODB_PASSWORD."
        except ServiceUnavailable:
            return False, "CognoDB is unreachable. Check COGNODB_URI and that the instance is running."
        except DatabaseUnavailableError as e:
            return False, str(e)
        except Exception as e:  # noqa: BLE001 - surfaced to the caller, not swallowed
            return False, f"Unexpected error connecting to CognoDB: {e}"

    @contextmanager
    def session(self):
        if self._driver is None:
            self.connect()
        session = self._driver.session()
        try:
            yield session
        finally:
            session.close()

    def run_read(self, cypher: str, parameters: dict[str, Any] | None = None) -> dict:
        """Run a parameterised read query.
        Returns {"rows": [...plain dicts for the table view...],
                 "graph": {"nodes": [...], "links": [...]}} extracted from
        any Node/Relationship/Path values the query returned.
        """
        try:
            with self.session() as session:
                result = session.run(cypher, parameters or {})
                rows = []
                nodes: dict[str, dict] = {}
                links: list[dict] = []
                for record in result:
                    rows.append(record.data())
                    for value in record.values():
                        _extract_graph(value, nodes, links)
                return {
                    "rows": rows,
                    "graph": {"nodes": list(nodes.values()), "links": links},
                }
        except ServiceUnavailable as e:
            raise DatabaseUnavailableError(f"CognoDB is unreachable: {e}") from e
        except AuthError as e:
            raise DatabaseUnavailableError(f"CognoDB authentication failed: {e}") from e

    def run_write(self, cypher: str, parameters: dict[str, Any] | None = None) -> list[dict]:
        """Run a parameterised write query (used only by the seed script)."""
        try:
            with self.session() as session:
                result = session.run(cypher, parameters or {})
                return [record.data() for record in result]
        except ServiceUnavailable as e:
            raise DatabaseUnavailableError(f"CognoDB is unreachable: {e}") from e
        except AuthError as e:
            raise DatabaseUnavailableError(f"CognoDB authentication failed: {e}") from e


graph_db = GraphDB()
