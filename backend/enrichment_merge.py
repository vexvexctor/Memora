import json
import datetime
import requests
import time

# Replace this with your real SerpAPI key
SERPAPI_KEY = '2b92365cefba8c6aecaeed214720a12cc70d3473de109600276e0d330261ec71'
SEARCH_URL = 'https://serpapi.com/search.json'

def load_data(*files):
    all_contacts = []
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            all_contacts.extend(data)
    return all_contacts

def normalize_email(email):
    return email.lower().strip() if email else None

def enrich_contact_online(contact):
    query = f"{contact['name']} {contact.get('email', '')} site:linkedin.com"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 1
    }
    try:
        response = requests.get(SEARCH_URL, params=params)
        data = response.json()
        snippet = data.get("organic_results", [{}])[0].get("snippet", "")
        title = data.get("organic_results", [{}])[0].get("title", "")

        if "unknown" in contact.get("tags", []) or not contact.get("tags"):
            tags = []
            for word in ["biology", "CS", "startup", "engineer", "research", "Harvard", "Stanford"]:
                if word.lower() in snippet.lower():
                    tags.append(word)
            if tags:
                contact["tags"] = tags

        if contact.get("profession") in [None, "unknown"] and title:
            contact["profession"] = title

    except Exception as e:
        print(f"Error enriching {contact['name']}: {e}")
    time.sleep(1.5)
    return contact

def enrich_and_merge(contacts):
    merged = {}
    for contact in contacts:
        email = normalize_email(contact.get("email"))
        name = contact.get("name", "").strip()
        key = email or name

        if key in merged:
            existing = merged[key]
            existing["source"] = list(set(existing["source"] + [contact.get("source", "unknown")]))
            for field in ["phone", "email", "profession"]:
                if not existing.get(field) and contact.get(field):
                    existing[field] = contact[field]
            existing["tags"] = list(set(existing.get("tags", []) + contact.get("tags", [])))
            existing["communication_count"] += contact.get("communication_count", 0)
            existing["last_contacted"] = max(existing.get("last_contacted") or "", contact.get("last_contacted") or "")
        else:
            merged[key] = {
                "name": name,
                "email": email,
                "phone": contact.get("phone"),
                "profession": contact.get("profession"),
                "tags": contact.get("tags", []),
                "source": [contact.get("source", "unknown")],
                "communication_count": contact.get("communication_count", 0),
                "last_contacted": contact.get("last_contacted"),
                "tightness_score": None,
                "social_channels": {},
                "notes": "",
                "updated": datetime.datetime.utcnow().isoformat()
            }

    merged_list = list(merged.values())

    # 🔍 Online enrichment for all contacts
    enriched = [enrich_contact_online(c) for c in merged_list]
    return enriched

if __name__ == "__main__":
    all_contacts = load_data("contacts_output.json", "gmail_output.json", "linkedin_output.json")
    merged_contacts = enrich_and_merge(all_contacts)
    with open("merged_contacts.json", "w") as f:
        json.dump(merged_contacts, f, indent=2)
