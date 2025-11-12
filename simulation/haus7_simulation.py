import random
from typing import Dict, List

class Haus7Simulation:
    def __init__(self, seed: int = 42):
        random.seed(seed)

    def score_campaigns(self, campaigns: List[Dict]) -> Dict:
        scored = []
        for c in campaigns:
            base = random.uniform(0.04, 0.09)
            ctr = base + (0.01 if "Video" in c["channel"] else 0.0)
            cvr = random.uniform(0.02, 0.06)
            cac = random.uniform(250.0, 600.0)
            risk_bias = 1 if "Exklusiv" in c["name"] else 0
            scored.append({**c, "ctr": ctr, "cvr": cvr, "cac": cac, "risk_bias": risk_bias})
        return {"scored_campaigns": scored}
