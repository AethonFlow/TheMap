from typing import Dict

class Haus2Produkt:
    def make_bundles(self, briefing: Dict) -> Dict:
        base = {"name":"Base","feature_level":0.4,"price_eur": 8900}
        premium = {"name":"Premium","feature_level":0.65,"price_eur": 11500}
        signature = {"name":"Signature","feature_level":0.85,"price_eur": 15000}
        return {"bundles":[base, premium, signature], "region_shortlist": briefing.get("region_shortlist", [])}
