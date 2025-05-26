```python
from fastapi import FastAPI
from pydantic import BaseModel
import networkx as nx
import os
from graph_engine import build_graph_from_contacts, query_graph_semantic

app = FastAPI()
GRAPH_PATH = "data/contact_graph.gpickle"

class ContactList(BaseModel):
    contacts: list
    query_tags: list = []

class Query(BaseModel):
    start_person: str
    query_text: str

@app.post("/upload_contacts")
async def upload_contacts(payload: ContactList):
    G = build_graph_from_contacts(payload.contacts, query_tags=payload.query_tags)
    nx.write_gpickle(G, GRAPH_PATH)
    return {"status": "graph_built", "nodes": len(G.nodes), "edges": len(G.edges)}

@app.post("/query")
async def query(payload: Query):
    if not os.path.exists(GRAPH_PATH):
        return {"error": "Graph not built yet"}
    G = nx.read_gpickle(GRAPH_PATH)
    results = query_graph_semantic(G, payload.start_person, payload.query_text)
    return {"results": results}
