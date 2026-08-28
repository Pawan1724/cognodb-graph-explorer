import re
from fastapi import HTTPException

# Disallowed cypher keywords (mutating operations)
BANNED_KEYWORDS = [
    "CREATE", "DELETE", "DETACH", "DROP", "SET", "REMOVE", "MERGE",
    "CALL", "LOAD", "APOC"
]

def validate_cypher(query: str):
    upper_query = query.upper()
    for word in BANNED_KEYWORDS:
        # Check if the word exists as a whole word
        if re.search(r'\b' + word + r'\b', upper_query):
            raise HTTPException(status_code=400, detail=f"Destructive operation '{word}' is not allowed in generated Cypher.")
    return True
