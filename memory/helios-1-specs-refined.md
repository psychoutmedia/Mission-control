# Helios-1: Refined Specifications with Market Research

*Updated: 2026-03-07*

## Market Context

### Industry Landscape (2026)
- **Market Size**: $5 trillion projected by 2050
- **Key Players**: Tesla Optimus, Figure AI, Boston Dynamics Electric Atlas, Unitree (China)
- **2026 Milestones**:
  - Tesla Optimus Gen 3: Q1 2026 reveal
  - Boston Dynamics Electric Atlas: Pilot at Hyundai's Georgia plant
  - Unitree: Targeting 10,000-20,000 unit shipments in 2026
  - Boston Dynamics: Targeting 30,000 units/year by 2028

### Productive Gap
- Current humanoid robots achieve **70-85% of human productivity** in structured manufacturing tasks
- Key limitation: Whole-body control, real-time adaptation, fleet learning

---

## Helios-1: Industrial Pioneer (Refined)

### Core Specifications

| Parameter | Original | Refined | Rationale |
|----------|----------|---------|-----------|
| **Height** | 5'10" | 5'10" ✓ | Human-scale for existing infrastructure |
| **Payload (sustained)** | 50kg | **30-40kg** | Competitors at 15-25kg; focus on agility over raw strength |
| **Payload (burst)** | 80kg | **50-60kg** | Peak lifting for short durations |
| **Runtime** | 8 hours | **4-6 hours** | Hot-swappable batteries (2 min swap); lighter battery = more mobile |
| **Speed** | — | **3 km/h** (walking) | Human walking pace |
| **Cost Target** | — | **$30-50K/unit** | 50% of Tesla Optimus projected price |

### Key Technologies

1. **Large Behavior Model (LBM)**
   - Unlike LLMs for language, LBMs learn whole-body movement patterns
   - Foundation behaviors: walking, grasping, balancing, reaching
   - Fleet learning: One robot learns → all improve

2. **Haptic Telepresence**
   - Human operators feel what the robot feels
   - Remote control with force feedback
   - Bridge: Full autonomy for routine + human-in-loop for edge cases

3. **Edge AI Computing**
   - On-board GPU (NVIDIA Jetson or custom)
   - Local inference for real-time control
   - Cloud sync for fleet learning

### Target Markets (Prioritized)

| Priority | Market | Use Case | TAM |
|----------|--------|----------|-----|
| 1 | **Manufacturing** | Assembly, inspection, material handling | $80B |
| 2 | **Logistics** | Warehouse picking, sorting | $50B |
| 3 | **Construction** | Bricklaying, drywall, painting | $40B |
| 4 | **Mining** | Underground inspection, transport | $20B |
| 5 | **Disaster Response** | Search & rescue, hazardous inspection | $10B |

### Competitive Positioning

| Competitor | Strength | Weakness | Helios-1 Advantage |
|------------|----------|----------|-------------------|
| **Tesla Optimus** | Scale, battery tech | No real product yet | Faster to market, specialized |
| **Figure AI** | AI-first approach | Limited payload | Higher payload, fleet learning |
| **Boston Dynamics** | Proven mobility | Expensive, industrial focus | 50% cost, autonomy-first |
| **Unitree** | Low cost (~$16K) | China-only, limited AI | US-based, better software |

### Differentiation Strategy

1. **Fleet Learning First** — Competitors build single robots; we build a learning network
2. **Telepresence Bridge** — Human-in-loop for complex tasks, full autonomy for routine
3. **Vertical Focus** — Manufacturing + logistics over general-purpose
4. **Open API** — Third-party developers can build behaviors

---

## Development Roadmap

### Phase 1 (Year 1): Foundation
- [ ] LBM architecture design
- [ ] Prototyping: locomotion + grasping
- [ ] 5 pilot units to manufacturing partners
- **Funding**: $10M seed

### Phase 2 (Year 2-3): Scale
- [ ] Full autonomy for 3+ manufacturing tasks
- [ ] 100 units deployed
- **Funding**: $50M Series A

### Phase 3 (Year 4+): Commercial
- [ ] Multi-industry deployment
- [ ] 1,000+ units
- **Funding**: $100M+ Series B

---

## Key Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Hardware delays | High | High | Partner with contract manufacturer |
| LBM training data | Medium | High | Simulation + telepresence data collection |
| Competitor faster | Medium | High | Focus on fleet learning moat |
| Regulation | Low | Medium | Engage early with OSHA, FDA |

---

## Next Steps

1. Define LBM architecture (research paper + prototype)
2. Identify manufacturing pilot partner
3. Build simulation environment (MuJoCo or Isaac Sim)
4. Draft technical spec for investor deck
