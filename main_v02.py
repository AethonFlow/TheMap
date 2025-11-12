import json
from datetime import datetime

from simulation.haus3_marketing import Haus3Marketing
from simulation.haus7_simulation import Haus7Simulation
from simulation.haus2_produkt import Haus2Produkt
from simulation.haus6_markt import Haus6Markt
from simulation.haus9_integrator import Haus9Integrator


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -----------------------------
# Rückkopplungen & Helfer
# -----------------------------

def pick_best_bundle(m_out):
    """Wählt bestes Bundle: zuerst nach revenue/deposits, sonst nach sentiment."""
    mf = m_out.get("market_feedback", [])
    if not mf:
        return None
    keys = mf[0].keys()
    if "revenue" in keys and "deposits" in keys:
        return max(mf, key=lambda m: (m.get("revenue", 0), m.get("deposits", 0), m.get("sentiment", 0)))
    return max(mf, key=lambda m: m.get("sentiment", 0))


def should_early_stop(history, min_streak=2):
    """Früher Abbruch, wenn min_streak mal in Folge GO."""
    if len(history) < min_streak:
        return False
    return all(rec["go"] for rec in history[-min_streak:])


def apply_feedback_to_bundles(bundles, feature_weight: float):
    """
    Rückkopplung (x): hebt Feature-Level leicht an, wenn feature_weight > 0.6.
    Maximaler Boost ~ +0.2 (gekappt).
    """
    boost = max(0.0, feature_weight - 0.6) * 0.5  # bis ~ +0.2
    out = []
    for b in bundles:
        bl = min(0.95, b["feature_level"] + boost)
        out.append({**b, "feature_level": round(bl, 3), "price_eur": b["price_eur"]})
    return out


def apply_budget_to_cac(scored_campaigns, budget_alloc: float):
    """
    Rückkopplung (p): reduziert CAC leicht bei höherem Budget (Lerneffekt).
    Skala: 0.5 -> neutral; 1.0 -> -10% CAC; 0.0 -> +10% CAC.
    """
    adj = 1.0 - 0.2 * (budget_alloc - 0.5)
    out = []
    for c in scored_campaigns:
        out.append({**c, "cac": round(c["cac"] * adj, 2)})
    return out


# -----------------------------
# Ein Δt-Zyklus
# -----------------------------

def one_cycle(h3, h7, h2, h6, integrator, feature_weight, budget_alloc):
    """
    Kampagnen -> Sim(Score+CAC-Adjust) -> Bundles(+x) -> Markt(try: +Budget) -> Integrator(+p)
    Gibt alle Teil-Outputs + Integrator-Ergebnis zurück.
    """
    # 1) Kampagnen & Scoring
    c_out = h3.propose_campaigns()
    s_raw = h7.score_campaigns(c_out["campaigns"])
    s_out = {"scored_campaigns": apply_budget_to_cac(s_raw["scored_campaigns"], budget_alloc)}

    # 2) Bundles & Rückkopplung x
    briefing = {"region_shortlist": ["Patagonien", "Island", "Namibia"], "positioning": "Luxury Adventure"}
    p_base = h2.make_bundles(briefing)
    bundles = apply_feedback_to_bundles(p_base["bundles"], feature_weight)
    p_out = {"bundles": bundles, "region_shortlist": p_base.get("region_shortlist", [])}

    # 3) Marktreaktion (kompatibel zu v0.2/v0.3)
    try:
        m_out = h6.respond(p_out["bundles"], s_out["scored_campaigns"], budget_alloc=budget_alloc)
    except TypeError:
        m_out = h6.respond(p_out["bundles"], s_out["scored_campaigns"])

    # 4) Integrator
    integ = integrator.symplectic_step(m_out["market_feedback"], s_out["scored_campaigns"], dt=1.0)

    return c_out, s_out, p_out, m_out, integ


# -----------------------------
# Session (mehrere Δt-Schritte)
# -----------------------------

def run_session(w=None, steps=5, label="default"):
    h3 = Haus3Marketing()
    h7 = Haus7Simulation(seed=42)
    h2 = Haus2Produkt()
    h6 = Haus6Markt(seed=43)
    h9 = Haus9Integrator(w=w)

    history = []
    feat = h9.x
