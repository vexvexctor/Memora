```python
from fastapi import FastAPI
from pydantic import BaseModel
import networkx as nx
import os
from graph_engine import build_graph
from query_engine import query_contacts

app = FastAPI()
GRAPH_PATH = "data/contact_graph.gpickle"

class ContactList(BaseModel):
    contacts: list

class Query(BaseModel):
    query_tags: list

@app.post("/upload_contacts")
async def upload_contacts(payload: ContactList):
    contacts = payload.contacts
    G = build_graph(contacts)
    nx.write_gpickle(G, GRAPH_PATH)
    return {"status": "graph_built", "nodes": len(G.nodes), "edges": len(G.edges)}

@app.post("/query")
async def query(payload: Query):
    if not os.path.exists(GRAPH_PATH):
        return {"error": "Graph not built yet"}
    G = nx.read_gpickle(GRAPH_PATH)
    results = query_contacts(G, payload.query_tags)
    return {"results": results}
```
