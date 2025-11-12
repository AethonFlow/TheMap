from typing import Dict, List

class Haus9Integrator:
    def __init__(self, w=None, budget_total=100_000):
        self.w = w or [0.5, 0.2, 0.2, 0.1]
        self.budget_total = budget_total
        self.x = {"feature_weight": 0.6, "price_idx": 0.6}
        self.p = {"budget_alloc": 0.5}

    def _estimate_aspects(self, market_feedback: List[Dict], scored_campaigns: List[Dict]) -> Dict:
        if not market_feedback:
            return {"gewinn":0,"ethik":0,"nachhalt":0,"prestige":0}

        # Gewinn jetzt aus revenue - deposits*cac_avg, normiert
        revenue = sum(m["revenue"] for m in market_feedback)
        deposits = sum(m["deposits"] for m in market_feedback)
        cac_avg = (sum(c["cac"] for c in scored_campaigns)/len(scored_campaigns)) if scored_campaigns else 400.0
        profit = max(0.0, revenue - deposits * cac_avg)

        # Normierung: ~ 15000 EUR als obere Verkaufspreis-Referenz, 50 Deposits als solider Run
        norm = 15000 * 50
        profit_norm = min(1.0, profit / max(1.0, norm))

        # Ethik: invertierter Risikoanteil
        risk_avg = (sum(c["risk_bias"] for c in scored_campaigns)/len(scored_campaigns)) if scored_campaigns else 0
        ethik = max(0.0, 1.0 - 0.5*risk_avg)

        # Nachhaltigkeit: Platzhalter
        nachhalt = 0.6

        # Prestige: Sentiment-Mittel
        prestige = sum(m["sentiment"] for m in market_feedback)/len(market_feedback)

        return {
            "gewinn": round(profit_norm,3),
            "ethik": round(min(1.0, ethik),3),
            "nachhalt": round(min(1.0, nachhalt),3),
            "prestige": round(min(1.0, prestige),3)
        }

    def _penalty(self, aspects: Dict) -> float:
        pen = 0.0
        if aspects["ethik"] < 0.5: pen += 0.2
        if aspects["prestige"] < 0.6: pen += 0.1
        # leicht strenger bei sehr niedrigem Gewinn
        if aspects["gewinn"] < 0.2: pen += 0.05
        return pen

    # hamiltonian() und symplectic_step() unverändert lassen


    def hamiltonian(self, aspects: Dict) -> float:
        J = [aspects["gewinn"], aspects["ethik"], aspects["nachhalt"], aspects["prestige"]]
        H = sum(wi*Ji for wi,Ji in zip(self.w,J)) - self._penalty(aspects)
        return round(H,3)

    def symplectic_step(self, market_feedback: List[Dict], scored_campaigns: List[Dict], dt: float = 1.0) -> Dict:
        aspects = self._estimate_aspects(market_feedback, scored_campaigns)
        base_H = self.hamiltonian(aspects)

        df, dp = 0.02, 0.05
        self.x["feature_weight"] = min(1.0, max(0.0, self.x["feature_weight"] + df))
        H_fw = self.hamiltonian(self._estimate_aspects(market_feedback, scored_campaigns))
        self.x["feature_weight"] -= df

        self.p["budget_alloc"] = min(1.0, max(0.0, self.p["budget_alloc"] + dp))
        H_b = self.hamiltonian(self._estimate_aspects(market_feedback, scored_campaigns))
        self.p["budget_alloc"] -= dp

        if H_fw > base_H:
            self.x["feature_weight"] = min(1.0, self.x["feature_weight"] + df)
        if H_b > base_H:
            self.p["budget_alloc"] = min(1.0, self.p["budget_alloc"] + dp)

        go = (aspects["gewinn"] >= 0.5) and (aspects["prestige"] >= 0.6) and (aspects["ethik"] >= 0.5)

        return {
            "aspects": aspects,
            "H": self.hamiltonian(aspects),
            "state_x": self.x.copy(),
            "state_p": self.p.copy(),
            "go": go
        }
