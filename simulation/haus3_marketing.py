from typing import Dict, List

class Haus3Marketing:
    def propose_campaigns(self) -> Dict:
        campaigns = [
            {"name": "Expedition & Komfort", "hook": "Komfortabel ans Ende der Welt", "channel": ["Search","Video"]},
            {"name": "Mindful Luxury Adventure", "hook": "Stille, Sterne, Signature-Service", "channel": ["Social","Video"]},
            {"name": "Exklusiv & Club-Feeling", "hook": "Nur 10 Plätze – Ultra-Privat", "channel": ["Social","Direct"]}
        ]
        return {"campaigns": campaigns}
