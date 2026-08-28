from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import QuestionRequest, QAResponse
from .database import get_session
from .validators import validate_cypher
from .llm import generate_cypher, generate_answer

app = FastAPI(title="WorkGraph AI", description="Graph-powered AI Q&A API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "WorkGraph AI Backend is running."}

@app.get("/health")
def health_check():
    try:
        with get_session() as session:
            session.run("RETURN 1")
        db_status = "connected"
    except Exception:
        db_status = "unavailable"
    return {"status": "ok", "database": db_status}

@app.post("/ask", response_model=QAResponse)
def ask_question_legacy(request: QuestionRequest):
    """Compatibility wrapper for the original /api/qa endpoint used by the frontend.
    It forwards the request to the same logic as `ask_question`.
    """
    return ask_question(request)

@app.post("/api/qa", response_model=QAResponse)
def ask_question(request: QuestionRequest):
    question = request.question
    
    # 1. Translate NL to Cypher
    try:
        cypher_query = generate_cypher(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error generating Cypher: {str(e)}")

    # 2. Validate Cypher
    validate_cypher(cypher_query)

    # 3. Execute Cypher
    try:
        with get_session() as session:
            result = session.run(cypher_query)
            graph_data = [record.data() for record in result]
            
            # Extract nodes and relationships for graph visualization
            # result.graph() aggregates all nodes/rels returned across all records
            graph_obj = result.graph()
            nodes = [{"id": n.element_id, "labels": list(n.labels), "properties": dict(n.items())} for n in graph_obj.nodes]
            links = [{"source": r.start_node.element_id, "target": r.end_node.element_id, "type": r.type} for r in graph_obj.relationships]
            graph_viz = {"nodes": nodes, "links": links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    # 4. Generate Answer
    try:
        answer = generate_answer(question, graph_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error generating answer: {str(e)}")

    return QAResponse(
        question=question,
        cypher_query=cypher_query,
        graph_data=graph_data,
        graph_viz=graph_viz,
        answer=answer
    )
