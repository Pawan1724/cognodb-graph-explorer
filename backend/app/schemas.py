from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QuestionRequest(BaseModel):
    question: str

class QAResponse(BaseModel):
    question: str
    # Expose the generated Cypher under the name the UI expects.
    cypher: str = Field(alias="cypher_query")
    # Alias existing `graph_data` field to `graph` for the UI.
    graph: List[Dict] = Field(default_factory=list, alias="graph_data")
    # Added for passing Neo4j graph structure for GraphView visualization
    graph_viz: Optional[Dict] = None
    # Empty rows list – UI will render a table if present.
    rows: List[Dict] = Field(default_factory=list)
    explanation: Optional[str] = None
    answer: str

    class Config:
        # Pydantic v2 renamed this key.
        populate_by_name = True

