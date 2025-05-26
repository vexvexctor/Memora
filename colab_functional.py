# Install dependencies
!pip install -q networkx sentence-transformers 

# Imports
import networkx as nx
from sentence_transformers import SentenceTransformer, util

# Load semantic embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# --- Utility Functions ---
def extract_query_topic(text):
    for preposition in ["with", "in", "on", "about", "regarding"]:
        if preposition in text:
            return text.split(preposition, 1)[1].strip()
    return text.strip()

def tag_match_score(query_tags, contact_tags):
    if not query_tags or not contact_tags:
        return 0.0
    q = set(query_tags)
    c = set(contact_tags)
    return round(len(q & c) / len(q | c), 3) if q | c else 0.0

def get_tightness(user_defined=None, freq_of_contact=None, last_contacted_days=None, clamp=True, min_val=0.05, max_val=1.0):
    if user_defined is not None:
        score = float(user_defined)
    elif freq_of_contact is not None and last_contacted_days is not None:
        recency_score = max(0.0, 1.0 - last_contacted_days / 365.0)
        freq_score = min(1.0, freq_of_contact / 20.0)
        score = freq_score * recency_score
    else:
        score = 0.25
    return round(min(max(score, min_val), max_val), 3) if clamp else round(score, 3)

def get_domain_match_semantic(query_text, contact_profession, contact_tags):
    contact_text = f"{contact_profession} {' '.join(contact_tags)}"
    embeddings = embedder.encode([query_text, contact_text], convert_to_tensor=True)
    return round(util.cos_sim(embeddings[0], embeddings[1]).item(), 3)

def compute_recommendation_score(cost, domain_match, max_cost=100.0):
    if cost >= 1e6:
        return 0.0
    cost_score = 1 - min(cost / max_cost, 1.0)
    return round((domain_match + cost_score) / 2, 3)

# --- Graph Construction ---
def create_contact_graph():
    return nx.DiGraph()

def add_contact_node(G, contact):
    G.add_node(contact["name"], **contact)

def connect_contacts(G, name1, name2, query_tags=None, domain_threshold=0.2, alpha=1.5, min_tightness=0.05, max_cost=100.0):
    p1 = G.nodes[name1]
    p2 = G.nodes[name2]
    prof_score = get_domain_match_semantic(p1["profession"], p2["profession"], [])
    tag_score = tag_match_score(query_tags or [], p2.get("tags", []))
    domain_match = (prof_score + tag_score) / 2
    raw_tightness = get_tightness(
        user_defined=p1.get("user_defined_tightness"),
        freq_of_contact=p1.get("freq_of_contact"),
        last_contacted_days=p1.get("last_contacted_days")
    )
    tightness = max(raw_tightness, min_tightness)
    if domain_match < domain_threshold:
        cost = 1e6
    else:
        epsilon = 0.01
        cost = 1 / (tightness ** alpha + epsilon)
        cost = round(min(cost, max_cost), 3)
    G.add_edge(name1, name2, cost=cost, tightness=raw_tightness, domain_match=domain_match)

def build_graph_from_contacts(contact_list, query_tags=None, domain_threshold=0.2, alpha=1.5):
    G = create_contact_graph()
    for c in contact_list:
        add_contact_node(G, c)
    for i in range(len(contact_list)):
        for j in range(len(contact_list)):
            if i != j:
                connect_contacts(G, contact_list[i]["name"], contact_list[j]["name"], query_tags, domain_threshold, alpha)
    return G

# --- Semantic Query Execution ---
def query_graph_semantic(graph, start_person, raw_query, top_k=3, domain_threshold=0.2):
    query_domain = extract_query_topic(raw_query)
    try:
        path_costs, paths = nx.single_source_dijkstra(graph, start_person, weight='cost')
    except nx.NetworkXNoPath:
        return []

    results = []
    for target in path_costs:
        if target == start_person:
            continue
        contact = graph.nodes[target]
        domain_match = get_domain_match_semantic(query_domain, contact["profession"], contact.get("tags", []))
        if domain_match >= domain_threshold:
            cost = path_costs[target]
            score = compute_recommendation_score(cost, domain_match)
            results.append((target, score, cost, domain_match, paths[target]))
    results.sort(key=lambda x: -x[1])
    return results[:top_k]

# --- Example Data ---
example_contacts = [
    {"name": "You", "profession": "student entrepreneur", "tags": ["MIT", "biotech"], "freq_of_contact": None, "last_contacted_days": None},
    {"name": "Alice", "profession": "biotech VC", "tags": ["startups", "healthcare", "VC"], "freq_of_contact": 10, "last_contacted_days": 45},
    {"name": "Bob", "profession": "software engineer", "tags": ["AI", "MIT", "startups"], "freq_of_contact": 5, "last_contacted_days": 120},
    {"name": "Charlie", "profession": "medtech founder", "tags": ["biotech", "diagnostics"], "freq_of_contact": 3, "last_contacted_days": 90},
    {"name": "Dana", "profession": "journalist", "tags": ["healthcare", "policy"], "freq_of_contact": 2, "last_contacted_days": 200}
]

# --- Build Graph + Run Example Query ---
G = build_graph_from_contacts(example_contacts, query_tags=["biotech", "VC", "startup"])
results = query_graph_semantic(G, start_person="You", raw_query="I need someone who can help me with biotech investing")

for name, score, cost, domain, path in results:
    print(f" {name}\n   Score: {score}\n   Cost: {cost}\n   Domain Match: {domain}\n")
