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

def run_cycle():
    h3 = Haus3Marketing()
    h7 = Haus7Simulation(seed=42)
    h2 = Haus2Produkt()
    h6 = Haus6Markt(seed=43)
    h9 = Haus9Integrator()

    c_out = h3.propose_campaigns()
    s_out = h7.score_campaigns(c_out["campaigns"])

    briefing = {"region_shortlist":["Patagonien","Island","Namibia"], "positioning":"Luxury Adventure"}
    p_out = h2.make_bundles(briefing)

    m_out = h6.respond(p_out["bundles"], s_out["scored_campaigns"])

    integ = h9.symplectic_step(m_out["market_feedback"], s_out["scored_campaigns"], dt=1.0)

    save_json('io/house3_out.json', c_out)
    save_json('io/house7_out.json', s_out)
    save_json('io/house2_out.json', p_out)
    save_json('io/house6_out.json', m_out)
    save_json('io/integrator_out.json', integ)

    ts = datetime.now().strftime('%Y-%m-%d %H:%M')
    report = []
    report.append(f'# Δt-Report – Prototyp v0.1  ({ts})')
    report.append('')
    report.append('## Aspekte (Schätzung)')
    A = integ['aspects']
    report += [f'- Gewinn: {A["gewinn"]}',
               f'- Ethik/PC: {A["ethik"]}',
               f'- Nachhaltigkeit: {A["nachhalt"]}',
               f'- Prestige: {A["prestige"]}',
               f'- Hamiltonian H: {integ["H"]}']
    report.append('')
    report.append('## State (x, p)')
    report += [f'- feature_weight: {integ["state_x"]["feature_weight"]}',
               f'- budget_alloc: {integ["state_p"]["budget_alloc"]}']
    report.append('')
    report.append('## Entscheidung')
    report.append('- GO' if integ['go'] else '- NO-GO (weiter justieren)')
    report.append('')
    report.append('---')
    txt = '\n'.join(report)
    with open('reports/run_latest.md','w', encoding='utf-8') as f:
        f.write(txt)

    print('\n'.join(report))

if __name__ == '__main__':
    run_cycle()
