# CAD-Bauplan (Systemskizze)

\\\mermaid
flowchart LR
    A2[Haus 2: Produkt] <--> I9((Haus 9: Integrator))
    A3[Haus 3: Marketing] <--> B7[Haus 7: Simulation/Komplementar]
    A2 --> A6[Haus 6: Markt (Sim v1)]
    A3 --> A6
    A6 -- Feedback (KPIs, Sentiment) --> A2
    I9 -- Takt Δt, symplectic_step --> A2 & A3 & B7 & A6
\\\

**Hinweis:** v1: Markt (Haus 6) ist synthetisch; Echtbetrieb folgt.
