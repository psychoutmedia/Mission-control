# Helios-1: Industrial Humanoid Technical Specification
**Automa Dynamics — Confidential**
**Version:** 0.3 | **Date:** 2026-04-16 | **Status:** Draft

---

## Executive Summary

Helios-1 is a 5'10" industrial humanoid robot designed for dangerous, dull, and distanced work. It combines a Large Behavior Model (LBM) for whole-body control with haptic telepresence, enabling both autonomous operation and human-in-the-loop oversight. Fleet learning allows experience from one unit to benefit the entire fleet instantly.

---

## Hardware Specifications

### Dimensions & Structure

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Height** | 5'10" (178 cm) | Human-scale for existing infrastructure |
| **Weight** | 85 kg | Heavy enough for stability, light enough for portability |
| **Chassis** | Aluminum + carbon fiber composite | High strength-to-weight ratio |
| **Degrees of Freedom** | 32 total | 2 legs (6 each), 2 arms (7 each), torso (3), head (3) |
| **Hand Dexterity** | 20 DOF per hand | Precision manipulation |

### Payload & Power

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Sustained Payload** | 50 kg | Continuous operation under load |
| **Burst Payload** | 80 kg | Short-term heavy lifting |
| **Runtime** | 8 hours | Full shift with hot-swappable batteries |
| **Battery** | 48V lithium iron phosphate (LiFePO4) | 2× 2kWh packs, hot-swap in <60 seconds |
| **Charging** | 80% in 30 min | Rapid turnaround |

### Mobility

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Max Speed** | 4.5 km/h (walk), 12 km/h (run) | Human-comparable movement |
| **Climbing** | Stairs up to 35° incline | Standard industrial staircases |
| **Terrain** | Unpaved, 5cm obstacles | Construction site adaptability |
| **Standing Balance** | 100 kg push recovery | Withstands industrial bumping |
| **Fall Recovery** | Autonomous get-up in <10 seconds | Minimal downtime |

### Sensing Suite

| Sensor | Quantity | Purpose |
|--------|----------|---------|
| **RGB-D Camera** | 3× (head + wrists) | Depth perception, manipulation |
| **LiDAR** | 1× (head, 360°) | Long-range obstacle detection |
| **IMU** | 1× (torso) | Balance and orientation |
| **Force/Torque** | 6× (bilateral hands + feet) | Grasp force, ground contact |
| **Tactile Arrays** | 2× (palms) | Fine touch feedback |
| **Microphone Array** | 4× | Speech recognition, sound localization |
| **Temperature** | 12× (joint motors) | Thermal monitoring |

### Computation

| Component | Spec | Purpose |
|-----------|------|---------|
| **Main Compute** | NVIDIA Jetson Thor (200 TOPS) | Real-time inference |
| **Safety Controller** | Dedicated RISC-V MCU | Failsafe, hard realtime |
| **Connectivity** | 5G + WiFi 7 + Wired | Fleet coordination, telepresence |
| **Local Storage** | 2TB NVMe | Edge model caching |

---

## Software Architecture

### 1. Large Behavior Model (LBM)

The LBM is the neural network that controls Helios-1's entire body — not just individual motions but coordinated whole-body behavior.

**Architecture:**
- **Base:** Causal transformer (similar to LLM but outputs motor commands)
- **Input:** Sensor fusion (cameras, proprioception, IMU, force feedback)
- **Output:** Target joint positions at 100Hz
- **Training:** Imitation learning from human demonstrations + RL for refinement
- **Model Size:** ~7B parameters (quantized to INT4 for edge deployment)

**Key Capabilities:**
- Zero-shot generalization to novel objects
- Continuous skill learning from human feedback
- Anomaly detection (unusual situations trigger fallback/telepresence)

**Training Pipeline:**
```
Human Telepresence → Motion Capture → Pre-training (imitation)
                                         ↓
                               Real-world self-play (RL)
                                         ↓
                               Fleet distillation (emergent behaviors)
```

### 2. Fleet Learning System

When one Helios learns, the fleet benefits instantly.

**Architecture:**
- **Edge:** Each unit runs inference locally (low latency, no cloud dependency)
- **Upload:** Anonymized experience tuples (state → action → outcome) compressed and sent
- **Aggregation:** Server-side federated learning — gradient updates without raw data
- **Distribution:** Updated model weights broadcast to all units

**Privacy:** Raw sensor data never leaves the robot. Only behavioral embeddings are shared.

**Update Cadence:** Critical safety fixes push immediately; capability improvements batch daily.

### 3. Haptic Telepresence

Human operators can take direct control with full sensory feedback.

**Latency Target:** <50ms round-trip (operator action → robot response → haptic feedback)

**Operator Station:**
- VR/AR headset (visual + spatial audio)
- Haptic gloves (force feedback on fingers)
- Exosuit or haptic vest (body awareness)
- Voice commands for high-level directives

**Mode Switching:**
- Smooth handoff between autonomous and telepresence
- Override command always available (emergency stop)
- "Shadow mode" — AI assists human operator in real-time

### 4. Safety System

**Layers:**

1. **Hardware Failsafe:** Dedicated MCU with independent power and sensors
2. **Software Limits:** Joint position/velocity/acceleration limits enforced at 1000Hz
3. **Collision Detection:** Immediate torque reduction on unexpected contact
4. **Behavioral Monitor:** LBM outputs checked against safety envelope
5. **Remote Override:** Human supervisor can halt any unit instantly

**Certifications (Target):**
- ISO 10218-1/2 (industrial robot safety)
- ISO/TS 15066 (collaborative robots)
- CE, UL, CSA

---

## Autonomy Levels

| Level | Name | Description |
|-------|------|-------------|
| **L1** | Remote Control | Human teleoperates full-time |
| **L2** | Assist Mode | AI assists human, human supervises |
| **L3** | Conditional Autonomy | AI handles routine tasks, human on-demand |
| **L4** | High Autonomy | AI handles all standard operations |
| **L5** | Full Autonomy | No human intervention required (future) |

**Initial Deployment:** L2/L3 with L1 fallback always available.

---

## Target Markets & Use Cases

### Phase 1 (Years 1-3)

| Market | Use Case | Priority |
|--------|----------|----------|
| **Manufacturing** | Assembly line tasks, quality inspection, machine tending | P0 |
| **Logistics** | Warehouse picking, packing, inventory management | P0 |
| **Construction** | Material handling, tool delivery, site monitoring | P1 |
| **Mining** | Underground material transport, repetitive extraction | P1 |

### Phase 2 (Years 3-5)

| Market | Use Case | Priority |
|--------|----------|----------|
| **Disaster Response** | Search & rescue, hazardous material handling | P1 |
| **Agriculture** | Harvesting, planting, crop monitoring | P2 |
| **Healthcare** | Hospital logistics, patient transport | P2 |

---

## Competitive Differentiation

| Competitor | Helios-1 Advantage |
|------------|---------------------|
| **Boston Dynamics (Atlas)** | Purpose-built for industrial, not research; fleet learning; affordable |
| **Figure AI** | Longer runtime; haptic telepresence; LBM approach |
| **Agility Robotics (Digit)** | Greater payload; hotter operating range; modular end-effectors |
| **Tesla (Optimus)** | Automa's focus is 100% humanoid; faster iteration; enterprise-first |

**Key Moat:**
1. Fleet learning network effects
2. LBM architecture optimized for industrial tasks
3. Haptic telepresence for seamless human-robot collaboration
4. Enterprise-grade safety certifications

---

## Development Roadmap

### Year 1 (2026)
- [ ] Prototype v0.1: Basic locomotion, pick-and-place
- [ ] LBM v1: Single-task imitation learning
- [ ] Telepresence system: Lab validation
- [ ] Safety audit: ISO 10218 compliance review
- [ ] Pilot units: 5 deployed with partner manufacturer

### Year 2 (2027)
- [ ] Prototype v0.3: Full 32-DOF, improved balance
- [ ] LBM v2: Multi-task, fleet learning enabled
- [ ] Production design: Cost-reduced for manufacturing
- [ ] Scale: 50 units deployed
- [ ] Series A: $50M raise

### Year 3 (2028)
- [ ] Commercial v1.0: Full production release
- [ ] LBM v3: Zero-shot generalization improved
- [ ] Scale: 100+ units, 3 enterprise customers
- [ ] Series B: $100M raise

### Years 4-6 (2029-2031)
- [ ] L4 autonomy for standard tasks
- [ ] 1,000+ units deployed
- [ ] $100M ARR milestone

### Years 7-10 (2032-2035)
- [ ] L5 research and development
- [ ] 10,000+ units
- [ ] $1B ARR milestone

---

## Financial Projections

| Metric | Year 2 | Year 3 | Year 5 | Year 7 | Year 10 |
|--------|--------|--------|--------|--------|---------|
| **Units Deployed** | 50 | 150 | 1,000 | 10,000 | 100,000 |
| **Avg Revenue/Unit** | $150K | $140K | $120K | $100K | $80K |
| **ARR** | $8M | $21M | $120M | $1B | $8B |
| **Cumulative Funding** | $60M | $160M | $500M | — | — |

*Assumptions: Hardware margin improves with scale; software/subscription revenue grows faster than hardware*

---

## Technical Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-------------|--------|------------|
| LBM training fails to generalize | Medium | High | Fallback to telepresence for edge cases; iterative RL |
| Fleet learning privacy concerns | Low | Medium | Federated learning; differential privacy |
| Battery technology limitations | Medium | Low | Hot-swap mitigates; alternative chemistries |
| Safety certification delays | High | Medium | Start certification process early; partner with TÜV |
| Hardware cost too high | High | High | Aggressive cost engineering; volume-based pricing |
| Competitor moves faster | Medium | High | Focus on fleet learning moat; iterate fast |

---

## Appendix: Glossary

- **DOF:** Degrees of Freedom — number of independent movements
- **LBM:** Large Behavior Model — transformer model for robot control
- **Fleet Learning:** Collective learning across all deployed units
- **Haptic Telepresence:** Full-body remote control with sensory feedback
- **Imitation Learning:** Training from human demonstrations
- **RL:** Reinforcement Learning — learning from rewards
- **Federated Learning:** Distributed training without sharing raw data
- **TOPS:** Trillion Operations Per Second — AI compute metric

---

*Automa Dynamics — Building capabilities that amplify human potential.*
*Next review: 2026-05-01*
