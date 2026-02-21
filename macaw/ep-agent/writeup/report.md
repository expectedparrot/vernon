# Ultimatum Game Study: LLM Behavioral Analysis

**Study Date:** February 21, 2026  
**Total Interviews:** 480 (6 personas × 20 scenarios × 4 models)  
**Results UUID:** c17670c4-0c1b-41d6-8c11-dcae79fdd315

---

## Executive Summary

This study investigates how Large Language Models (LLMs) play the ultimatum game, examining both proposer and responder behavior across different agent personas, contextual framings, and model architectures. We conducted 480 interviews using EDSL to simulate game-theoretic decision-making.

**Key Findings:**

1. **Persona Drives Behavior:** Agent personas exhibit dramatically different strategies—fairness-oriented agents offer perfect 50/50 splits, while self-interested agents offer minimal amounts (mean: $16.61).

2. **Model Differences Are Significant:** Claude models show higher acceptance rates than GPT models, particularly at low offer amounts (20.8% vs 45.8% acceptance for $20 offers).

3. **Clear Acceptance Threshold:** Acceptance rates jump from ~40% at $20-30 offers to 91.7% at $50 (equal split), suggesting strong fairness norms.

4. **Framing Has Minimal Effect:** Different contextual framings (business, charity, competitive, neutral) show surprisingly little variation in behavior.

---

## Research Questions

1. **How do LLMs split money as proposers in the ultimatum game?**
2. **What offers do LLMs accept/reject as responders?**
3. **Do different agent personas lead to different game-playing strategies?**
4. **Does framing (business, charity, competitive) affect behavior?**
5. **Do different LLM models exhibit different behavioral patterns?**

---

## Results

### 1. Proposer Behavior by Model

All models show bimodal distributions with peaks at extreme offers and 50/50 splits:

| Model | Mean Offer | Median | Std Dev | Min | Max |
|-------|------------|--------|---------|-----|-----|
| **Claude Sonnet 4.5** | $41.83 | $45.00 | $8.04 | $30 | $50 |
| **Claude Haiku 4.5** | $40.56 | $50.00 | $16.89 | $1 | $50 |
| **GPT-4o** | $36.81 | $50.00 | $20.32 | $1 | $50 |
| **GPT-4o-mini** | $36.12 | $50.00 | $24.75 | $1 | $99 |

**Key Observations:**
- Claude Sonnet shows the most consistent behavior (lowest std dev: 8.04)
- GPT-4o-mini has the highest variance and one outlier offer of $99
- All models have median offers at or near $50 (equal split)
- Mean offers are pulled down by low offers from self-interested personas

**Visualization:** See `plots/proposer_distribution.png`

---

### 2. Proposer Behavior by Agent Persona

Personas show starkly different proposer strategies:

| Persona | Mean Offer | Median | Std Dev | Strategy |
|---------|------------|--------|---------|----------|
| **Fairness-Oriented** | $50.00 | $50.00 | $0.00 | Perfect equality |
| **Justice-Focused** | $49.31 | $50.00 | $2.48 | Near-perfect equality |
| **Cooperative** | $49.06 | $50.00 | $1.96 | Highly generous |
| **Risk-Averse** | $47.56 | $50.00 | $2.64 | Generous to avoid rejection |
| **Competitive** | $20.42 | $30.00 | $16.51 | Low but varied |
| **Self-Interested** | $16.61 | $1.00 | $23.54 | Minimal offers |

**Key Observations:**
- Three personas (fairness, justice, cooperative) cluster at near-perfect 50/50 splits
- Risk-averse agents offer slightly less but still very generous (~$47.56)
- Competitive and self-interested personas offer dramatically less
- Self-interested has highest variance—some models override the persona toward fairness

**Visualization:** See `plots/persona_comparison.png`

---

### 3. Responder Acceptance Rates by Offer Amount

Clear threshold effect around the equal split:

| Offer Amount | Overall Acceptance | Accepts | Total |
|--------------|-------------------|---------|-------|
| **$20 (20%)** | 40.6% | 39/96 | Mostly rejected |
| **$30 (30%)** | 41.7% | 40/96 | Mostly rejected |
| **$40 (40%)** | 51.0% | 49/96 | Marginal |
| **$50 (50%)** | 91.7% | 88/96 | Strong acceptance |
| **$60 (60%)** | 85.4% | 82/96 | High acceptance |

**Key Observations:**
- Sharp discontinuity between $40 and $50 offers
- Equal split ($50) achieves near-universal acceptance (91.7%)
- Above-equal offers ($60) slightly less accepted—possible suspicion/confusion
- Below 40% share, offers are rejected more than half the time

**Visualization:** See `plots/acceptance_curve.png`

---

### 4. Model-Specific Acceptance Patterns

Acceptance rates vary significantly by model:

| Offer | Claude Haiku | Claude Sonnet | GPT-4o | GPT-4o-mini |
|-------|--------------|---------------|--------|-------------|
| **$20** | 45.8% | 54.2% | 37.5% | **20.8%** |
| **$30** | 45.8% | 50.0% | 37.5% | **25.0%** |
| **$40** | 70.8% | 66.7% | 50.0% | **33.3%** |
| **$50** | 95.8% | **100.0%** | 91.7% | 70.8% |
| **$60** | **100.0%** | 95.8% | 83.3% | 75.0% |

**Key Observations:**
- **Claude models are more accepting** across all offer levels
- **GPT-4o-mini is most rejecting**, particularly at unfair offers
- Claude Sonnet accepts 100% of equal splits
- Model choice matters more at unfair offer levels ($20-40)

**Visualization:** See `plots/acceptance_curve.png`

---

### 5. Framing Effects

We tested four contextual framings:

| Framing Type | Mean Proposer Offer | Acceptance Rate |
|--------------|-------------------|-----------------|
| **Business** | $38.73 | 61.7% |
| **Charity** | $38.78 | 62.5% |
| **Competitive** | $38.52 | 60.8% |
| **Neutral** | $38.48 | 60.8% |

**Key Observations:**
- Framing effects are **minimal** (all within $0.30 range)
- Acceptance rates vary by only ~2 percentage points
- Suggests LLMs apply consistent fairness heuristics regardless of context
- This contrasts with human studies showing stronger framing effects

**Visualization:** See `plots/framing_effect.png`

---

## Discussion

### Persona as Primary Driver

The most striking finding is how strongly agent personas determine behavior. When instructed to embody a "fairness-oriented" persona, all LLMs offer exactly $50 with zero variance. When instructed to be "self-interested," offers drop to ~$16 with high variance. This suggests:

1. **LLMs can reliably adopt different behavioral strategies** when given clear role instructions
2. **Persona framing overrides model-specific tendencies** in most cases
3. **Some personas conflict with model training** (high variance for self-interested)

### Model Architectural Differences

Claude and GPT models show distinct patterns:

- **Claude models** are more accepting of unfair offers, possibly reflecting:
  - Different training on cooperation/politeness
  - Higher tolerance for inequality
  - Less strong fairness norms

- **GPT-4o-mini** is notably more rejecting, possibly due to:
  - Stronger distillation of fairness principles
  - More rigid decision boundaries
  - Different RLHF training

### The $50 Threshold

The 91.7% acceptance rate at $50 (equal split) is consistent with:

1. **Strong fairness norms** in LLM training data
2. **Game-theoretic rational acceptance** (something > nothing)
3. **Social contract reasoning** embedded in models

The slight drop at $60 (85.4%) is intriguing—possibly reflecting:
- Suspicion about overly generous offers
- Confusion about the game rules
- Preference for equality over advantage

### Framing Resistance

The lack of framing effects is surprising given human behavioral economics literature. Possible explanations:

1. **Abstraction over surface features:** LLMs may identify the underlying game structure regardless of framing
2. **Training data averaging:** Models trained on diverse contexts may wash out framing effects
3. **Insufficient framing strength:** Our framings may need to be more extreme

---

## Limitations

1. **LLMs vs Humans:** These are artificial agents, not human players
2. **Single-shot game:** No reputation or repeated game dynamics
3. **No real stakes:** Hypothetical money doesn't create genuine incentives
4. **Persona effects:** Results heavily dependent on how personas are specified
5. **Sample size:** Only 80 interviews per persona (could increase statistical power)

---

## Implications

### For AI Safety

- LLMs can adopt different ethical frameworks when instructed
- Persona instructions have stronger effects than contextual framing
- Models show different baseline fairness norms

### For Game Theory Research

- LLMs provide a new experimental platform for testing strategic behavior
- Can simulate populations with controlled trait distributions
- Enable rapid hypothesis testing at scale

### For Model Comparison

- Claude and GPT show measurably different behavioral patterns
- Model choice matters for applications requiring negotiation or fairness
- Smaller models (GPT-4o-mini) aren't just less capable—they're behaviorally different

---

## Conclusions

This study demonstrates that:

1. **LLMs exhibit coherent game-theoretic behavior** that varies systematically by persona and model
2. **Fairness norms are strong** across all models, with sharp acceptance thresholds at equal splits
3. **Persona instructions dominate** model-specific and contextual factors
4. **Model architecture matters** for behavioral applications beyond pure capability

Future work could explore:
- Repeated games and reputation effects
- Mixed-motive scenarios (not pure distributional conflicts)
- Cultural framings and demographic personas
- Multi-agent negotiations with diverse LLM populations

---

## Data Availability

- **Results:** `data/results.json.gz` (480 interviews)
- **Coop UUID:** `c17670c4-0c1b-41d6-8c11-dcae79fdd315`
- **Tables:** `writeup/tables/`
- **Visualizations:** `writeup/plots/`

---

## Reproducibility

To reproduce this analysis:

```bash
# Run the study
make run

# Generate all analysis
make analysis

# View results
ls writeup/tables/
ls writeup/plots/
```

All code, data, and analysis scripts are version-controlled in this study directory.
