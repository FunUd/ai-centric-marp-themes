---
name: slide-expert-tech-selection
description: Activate this skill ONLY when PLANNING or OUTLINING Tech Selection presentation slides. DO NOT activate during Marp implementation, layout fixing, or exporting.
---

# Technology Selection Comparison Slide Expert


## MANDATORY: Confirm Before Drafting

**DO NOT generate any slide content for a new or substantially revised deck until you have explicitly confirmed the outline with the user.**

Before writing any new slide content, you MUST:
1. Present a proposed outline (section titles + slide count + estimated time) based on the guidelines below.
2. Ask: "Does this structure work for you? Let me know if you'd like any changes."
3. Wait for explicit approval before proceeding.

## Core Principles

A technology selection slide deck must answer four questions:

1. **What problem are we solving?** - Context and requirements
2. **What options did we consider?** - Alternatives evaluated
3. **How do they compare?** - Evaluation criteria and trade-offs
4. **What are we choosing and why?** - Recommendation with rationale

## Slide Structure Template

### 1. Context & Problem Statement (1-2 slides)
- Current challenge or pain point
- Business/technical requirements
- Constraints (budget, timeline, team skills)
- Success criteria

### 2. Options Overview (1 slide)
- Brief introduction of 2-4 alternatives
- Key characteristics per option (1-2 bullets)
- Include "status quo" option if relevant

### 3. Evaluation Criteria (1 slide)
Define 5-7 criteria from:
- **Functional**: Suitability, accuracy, interoperability
- **Quality**: Performance, security, scalability, maintainability
- **Organizational**: Team expertise, vendor support, community
- **Cost**: Initial cost, ongoing maintenance, scaling costs

### 4. Comparison Matrix (1-2 slides)
Side-by-side comparison using:
- **5-star scale**: ⭐ to ⭐⭐⭐⭐⭐
- **3-point scale**: ◎ (Good) / ○ (Fair) / △ (Poor)
- **Binary**: ✓ / ✗ for pass/fail criteria

Place most important criteria at the top.

### 5. Trade-off Analysis (1-2 slides)
Visualize inherent compromises:
- Performance vs. Cost
- Flexibility vs. Simplicity
- Time to Market vs. Perfection
- Innovation vs. Stability

Show which option wins under different priority scenarios.

### 6. Risk Assessment (1 slide)
| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| [Risk description] | Low/Med/High | Low/Med/High | [Specific action] |

### 7. Recommendation (1-2 slides)
Structure:
1. **The Decision**: State chosen option clearly
2. **Primary Reasons**: 3 bullets max
3. **Acknowledged Trade-offs**: 1-2 bullets
4. **Next Steps**: Immediate actions with timeline

### 8. Decision Record (Optional appendix)
ADR-style format:
- **Context**: Issue motivating the decision
- **Decision**: What we're implementing
- **Consequences**: What becomes easier/harder

## Content Guidelines

### Comparison Tables
- Use consistent rating system throughout
- Highlight recommended option (bold/color)
- Keep cell content brief
- Add footnotes for subjective criteria

### Trade-off Presentation
- Be honest about downsides of recommended option
- Show trade-offs were consciously considered
- Connect back to business priorities

### Recommendation Clarity
- Lead with the decision, not the analysis
- Connect to original requirements
- Include specific next steps and owners

## Quality Checklist

Content:
- [ ] Problem context clearly stated
- [ ] All viable alternatives presented
- [ ] Evaluation criteria explicit and relevant
- [ ] Comparison fair and balanced
- [ ] Trade-offs acknowledged
- [ ] Recommendation includes rationale
- [ ] Next steps actionable and specific

Visual:
- [ ] Tables fit within slide boundaries
- [ ] Rating symbols consistent
- [ ] Recommended option visually distinct
- [ ] No information overload (split if >6 criteria)


## Workflow Handoff

Once the content structure and text are finalized based on these guidelines, **DO NOT generate the final Marp Markdown directly from this skill**.
Instead, hand off the implementation to the `marp-slide-creator` skill to ensure proper Marp syntax, layout, and overflow prevention.

> **Diagram Warning for Implementation Phase:** When suggesting diagrams (like Sequence or Flowcharts), remind the user that inline Mermaid (` ```mermaid `) fails in Marp PDF exports. Diagrams must be placed as placeholder images (`![Diagram](./assets/diagram.svg)`) and generated offline using Mermaid CLI during the implementation phase.

