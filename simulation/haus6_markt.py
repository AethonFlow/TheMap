import random
from typing import Dict, List

class Haus6Markt:
    def __init__(self, seed: int = 43):
        random.seed(seed)

    def respond(self, bundles: List[Dict], scored_campaigns: List[Dict], budget_alloc: float = 0.5) -> Dict:
        # Kampagnenqualität
        if not scored_campaigns:
            quality = 0.03
            ctr_avg = 0.05
            cvr_avg = 0.03
            cac_avg = 400.0
            risk_avg = 0.0
        else:
            ctr_avg = sum(c['ctr'] for c in scored_campaigns) / len(scored_campaigns)
            cvr_avg = sum(c['cvr'] for c in scored_campaigns) / len(scored_campaigns)
            risk_avg = sum(c['risk_bias'] for c in scored_campaigns) / len(scored_campaigns)
            cac_avg = sum(c['cac'] for c in scored_campaigns) / len(scored_campaigns)
            quality = max(0.0, (ctr_avg + cvr_avg) - 0.5*risk_avg)

        # Reichweite ~ Budget & Qualität
        audience_size = int(1000 * (0.8 + 0.4*budget_alloc) * (0.5 + quality))  # 600..~1800

        resp = []
        for b in bundles:
            # Lead & Deposit
            lead_rate = max(0.0, min(0.25, quality*0.8 + 0.3*b["feature_level"]))
            deposit_rate = max(0.0, min(0.18, lead_rate*0.55))

            leads = int(audience_size * lead_rate)
            deposits = int(leads * deposit_rate)

            # Stimmung & Zahlungsbereitschaft
            sentiment = 0.55 + 0.3*b["feature_level"] - 0.05*random.random()
            wtp_mid = int(b["price_eur"] * (0.95 + 0.1*random.random()))

            # Umsatz & einfacher Gewinn-Proxy
            price = b["price_eur"]
            revenue = deposits * price
            cac_total = deposits * cac_avg
            profit_proxy = max(0.0, revenue - cac_total)  # *kein* Fixkostenmodell in v0.3

            resp.append({
                "bundle": b["name"],
                "feature_level": round(b["feature_level"],3),
                "lead_rate": round(lead_rate,4),
                "deposit_rate": round(deposit_rate,4),
                "leads": leads,
                "deposits": deposits,
                "sentiment": round(sentiment,3),
                "wtp_mid": wtp_mid,
                "price_eur": price,
                "revenue": int(revenue),
                "cac_avg": round(cac_avg,2),
                "profit_proxy": int(profit_proxy)
            })

        return {
            "market_feedback": resp,
            "audience_size": audience_size,
            "quality": round(quality,4),
            "ctr_avg": round(ctr_avg,4),
            "cvr_avg": round(cvr_avg,4),
            "risk_avg": round(risk_avg,4),
            "cac_avg": round(cac_avg,2)
        }
