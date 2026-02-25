---
name: literature-review
description: Gather and synthesize academic literature for a research question, then use findings to inform study design and analysis.
---

# Literature Review

Systematic process for finding academic resources relevant to a research question and using them to strengthen study design.

## When to use this skill

- At the start of a study, before writing `plan.md`
- When the user asks to ground their research in existing literature
- When designing survey instruments that should reference established constructs or scales
- When choosing analysis methods and needing precedent

## Step 1: Clarify the research question

Before searching, ensure you have a focused research question. Ask the user if needed. A good research question has:

- A clear **population or domain** (e.g., "US consumers", "software engineers", "LLM agents")
- A specific **phenomenon or relationship** (e.g., "willingness to pay for privacy", "effect of framing on choices")
- A defined **outcome or construct** (e.g., "purchase intent", "trust", "response quality")

Write the refined research question to `literature/research_question.md` in the study directory.

## Step 2: Search for literature

Use `WebSearch` to find relevant academic papers, working papers, and review articles. Run multiple searches with varied queries to get good coverage.

### Search strategy

Run at least 3-5 searches using different angles:

```
# Direct topic search
WebSearch: "{core topic}" site:scholar.google.com

# Key constructs + methodology
WebSearch: "{construct}" survey experiment methodology

# Established scales or measures
WebSearch: "{construct}" validated scale measurement instrument

# Recent reviews or meta-analyses
WebSearch: "{topic}" systematic review OR meta-analysis

# Domain-specific searches
WebSearch: "{topic}" site:ssrn.com
WebSearch: "{topic}" site:arxiv.org
WebSearch: "{topic}" site:nber.org
```

### What to look for

1. **Foundational papers** — Seminal work that defined the constructs or theory
2. **Methodological precedents** — Studies that used similar designs (surveys, experiments, conjoint, etc.)
3. **Validated instruments** — Established question scales or measurement approaches
4. **Recent work** — Papers from the last 3-5 years showing the current state of knowledge
5. **Contradictions or gaps** — Areas where findings conflict or where evidence is thin

## Step 3: Read and extract key information

For each promising source, use `WebFetch` to access the content where possible (preprints, open-access papers, abstracts). Extract:

- **Citation** (authors, year, title, venue)
- **Research question / hypothesis**
- **Method** (sample size, design, instruments used)
- **Key findings** (effect sizes, main results)
- **Relevance** (how it connects to the current study)

## Step 4: Write the literature summary

Create `literature/review.md` in the study directory with the following structure:

```markdown
# Literature Review: {Research Question}

## Overview
{2-3 paragraph synthesis of what the literature says about this topic}

## Key Themes

### Theme 1: {name}
{Summary of findings across papers}
- Source 1 (Author, Year): {key finding}
- Source 2 (Author, Year): {key finding}

### Theme 2: {name}
...

## Methodological Insights
{What methods have been used to study this? What worked well?
What sample sizes were typical? What validated scales exist?}

## Gaps and Opportunities
{What hasn't been studied? Where do findings conflict?
What would a new study contribute?}

## Implications for Study Design
{Specific recommendations for how to design the current study,
informed by the literature:}
- Suggested constructs to measure
- Recommended question types or scales
- Sample size considerations
- Potential confounds to control for
- Analysis approaches used in prior work

## References
{Full list of cited sources}
```

## Step 5: Connect to study design

After completing the review, use the findings to:

1. **Inform the plan** — Reference literature findings in `plan.md` to justify design choices
2. **Adopt validated measures** — Use established scales rather than inventing new questions where possible
3. **Set expectations** — Note expected effect sizes or base rates from prior work
4. **Identify controls** — Include covariates or conditions that the literature suggests matter
5. **Frame the contribution** — Articulate what the study adds beyond existing work

## File organization

```
study_root/
  literature/
    research_question.md    # Refined research question
    review.md               # Full literature review
    sources/                # (optional) saved PDFs or key excerpts
  plan.md                   # References literature findings
```

## Tips

- **Breadth first, then depth.** Start with broad searches to map the landscape, then drill into the most relevant papers.
- **Don't over-search.** 10-20 well-chosen sources are better than 50 superficial ones. Stop when you start seeing the same papers cited repeatedly.
- **Distinguish empirical from theoretical.** Note which sources report original data vs. which are reviews or opinion pieces.
- **Note methodology details.** Sample sizes, response rates, and effect sizes from prior work directly inform your study design.
- **Be honest about gaps.** If the literature is thin in an area, say so — that's a strong motivation for the study.
- **Use author names.** When searching, once you find a key paper, search for the authors' other work — they often have related studies.
