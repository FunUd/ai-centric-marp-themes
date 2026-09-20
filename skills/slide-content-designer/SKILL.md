---
name: slide-content-designer
description: Activate this skill ONLY when the deck needs planning, outlining, or major restructuring. DO NOT generate any Markdown slide content until the outline is explicitly approved by the user.
---

# Slide Content Designer

This skill provides a structured workflow for creating high-impact, persuasive, and crystal-clear presentation slides, focusing on **content depth, narrative structure, and readability**.

Use this skill whenever a user wants to create or edit a presentation, outline a talk, review slide structure, or needs help figuring out what to say in their slides.

If the outline is already approved and the work is mainly Marp implementation, layout repair, overflow cleanup, or export, skip this skill and go straight to `marp-slide-creator`.

> **Quality Bible:** Always consult `references/quality-guidelines.md` for in-depth principles on message-driven titles, narrative frameworks (SCQA, PREP, BAB, Pyramid), anti-bullet-point formatting, and the 3-second readability rule.
> 
> **Domain-Specific Outlines:** If the user wants to create a specific type of presentation (e.g., API Architecture, Progress Report, Tech Sharing), prioritize activating the corresponding `slide-expert-*` skill instead of this generic one. Do not load both simultaneously.

---

## MANDATORY: Confirm Before Drafting a New Outline

**DO NOT generate any final slide content or Marp Markdown until you have explicitly confirmed the outline with the user.**

Before writing any new slide content, you MUST:
1. Conduct Discovery 2.0 (clarify purpose, audience, and core proof).
2. Propose a structured outline (Slide # + **Message-driven Title** + Intended Layout + 2-3 Core Points).
3. Ask: *"Does this structure and narrative arc work for you? Let me know if you'd like any changes."*
4. Wait for explicit approval before proceeding.

---

## 1. Discovery 2.0: Deep Intake & Value Definition

Do not jump to outlining with superficial information. Even when the user's prompt seems detailed, verify these 4 pillars:

1. **The Goal (Action / Decision)**:
   - What must happen after this presentation? (e.g., Budget approved, architecture greenlit, team adoption, clear understanding)
2. **The Audience & Objections (WIIFM)**:
   - Who is in the room? (Executives, tech leads, cross-functional partners)
   - What is their biggest skepticism or concern? What's in it for them?
3. **The Core Takeaway (So What?)**:
   - What is the single sentence the audience must remember next week?
4. **Facts & Figures (Proof)**:
   - What concrete numbers, benchmarks, Before/After metrics, or real examples substantiate the claim? *(Ban vague claims like "improved performance" without metrics).*

---

## 2. Narrative Frameworks (Storytelling)

Choose one of the 4 proven narrative patterns based on presentation intent (see `references/quality-guidelines.md` for full details):

### Pattern A: SCQA (Problem-Solving & Project Proposals)
- **Situation**: Ground truth context everyone agrees on.
- **Complication**: The bottleneck, shift in environment, or blocker.
- **Question**: "How do we resolve this blocker effectively?"
- **Answer**: Your proposed solution and architecture.
- **Action & Impact**: Measurable expected outcomes and next steps.

### Pattern B: PREP (Tech Selection, Architecture Choices, Opinion)
- **Point**: The core recommendation/decision upfront.
- **Reason**: Underlying rationale, trade-offs evaluated.
- **Example / Proof**: Benchmark data, prototype results, case comparison.
- **Point**: Reiteration of conclusion with rollout strategy.

### Pattern C: Before-After-Bridge (Improvement, Refactoring, Tool Migration)
- **Before**: Current pain points, technical debt, wasted man-hours.
- **After**: The ideal future state (e.g., 60% faster deploys, zero downtime).
- **Bridge**: The roadmap, tooling, and migration steps to get there.

### Pattern D: Pyramid Principle (Executive Status Reports, Reviews)
- **Top Line Message**: Overall health and high-level takeaway.
- **Pillar 1 / 2 / 3 (MECE)**: 3 supporting pillars (e.g., Schedule, Quality, Cost).
- **Decisions Required**: Specific approvals requested from stakeholders.

---

## 3. The "So What?" Title Rule (MANDATORY)

Slide titles MUST NOT be generic noun topics (e.g., "Overview", "Architecture", "Status", "Conclusion").
**Titles must state the primary conclusion or takeaway of the slide.**

- ❌ Bad: `## System Architecture`
- ✅ Good: `## Microservices decouple release cycles, cutting deploy time by 60%`
- ❌ Bad: `## Performance Evaluation`
- ✅ Good: `## Go rewrite delivers 3.5x throughput reduction under 10k RPS load`
- ❌ Bad: `## Next Steps`
- ✅ Good: `## Complete phase 1 rollout by Q3 to unlock automated failover`

*Note: You may use category badges (`<span class="badge blue">Architecture</span>`) to preserve contextual tagging.*

---

## 4. Anti-Bullet-Point & Readability Standards

When planning content for each slide:
- **Magic Number 3**: Target 3 (maximum 4) core items per slide.
- **Keyword Labeling**: Ban raw bullet paragraphs. Enforce `**[Key Label]**: Brief explanation`.
- **Structural Mapping**:
  - Parallel comparisons → Propose `cols-2` / `cols-3` or `split-2`.
  - Sequential workflows → Propose `steps` or `timeline`.
  - Matrices / Quadrants → Propose `grid-quadrant`.
- **Target Density**: Plan for 200–350 characters total per content slide. Excess text belongs in presenter notes (`<!-- notes -->`).

---

## 5. Standard Workflow Execution

1. **Clarify & Intake**: Allotted time (default 1 min/slide for business, 2 min/slide for technical), audience, core takeaway, and target output format (HTML/PDF/PPTX).
2. **Propose Storyline & Outline**:
   Present an outline formatted as:
   ```markdown
   ### Proposed Outline ([Framework Name], [N] Slides, ~[X] Mins)
   
   1. [Cover]: Title + Subtitle
   2. [Executive Summary / Hook]: So What? statement
   3. [Section 1 Title (Conclusion-driven)]: Proposed layout (e.g., cols-2) + 3 key points
   ...
   ```
3. **Visual Check Opt-in**: Ask: *"Would you like to perform visual layout checks using AI vision later? (High quality, but higher token cost) or stick to text-based linting?"*
4. **WAIT for Approval**: Do not write slide Markdown until confirmed.
5. **Handoff to `marp-slide-creator`**: Once confirmed, invoke `marp-slide-creator` to generate production-ready Marp Markdown.
