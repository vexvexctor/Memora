```python
import json
from collections import defaultdict
import datetime

def load_data(*files):
    all_contacts = []
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
            all_contacts.extend(data)
    return all_contacts

def normalize_email(email):
    return email.lower().strip() if email else None

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

    for contact in merged.values():
        if not contact["tags"]:
            contact["tags"].append("unknown")
        if not contact["profession"]:
            contact["profession"] = "unknown"

    return list(merged.values())

if __name__ == "__main__":
    all_contacts = load_data("contacts_output.json", "gmail_output.json", "linkedin_output.json")
    merged_contacts = enrich_and_merge(all_contacts)
    with open("merged_contacts.json", "w") as f:
        json.dump(merged_contacts, f, indent=2)
