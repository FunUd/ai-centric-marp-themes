---
name: slide-content-designer
description: Activate this skill ONLY when the deck needs planning, outlining, or major restructuring. DO NOT generate any Markdown slide content until the outline is explicitly approved by the user.
---

# Slide Content Designer

This skill provides a structured workflow for creating high-quality presentation slides, focusing on the planning and structuring phase.

Use this skill whenever a user wants to create or edit a presentation, outline a talk, review slide structure, or needs help figuring out what to say in their slides.

If the outline is already approved and the work is mainly Marp implementation, layout repair, overflow cleanup, or export, skip this skill and go straight to `marp-slide-creator`.

If the presentation details are incomplete or unclear, load this skill first and use it to clarify the audience, theme, format, slide count, and allotted time before drafting.

> **Note:** This skill focuses on *content, structure, and design principles*. For Marp-specific Markdown generation, use `marp-slide-creator` after the outline is finalized.
> 
> **Domain-Specific Outlines:** If the user wants to create a specific type of presentation (e.g., API Architecture, Progress Report, Tech Sharing), prioritize activating the corresponding `slide-expert-*` skill instead of this generic one. Do not load both simultaneously.

## MANDATORY: Confirm Before Drafting a New Outline

**DO NOT generate any slide content for a new or substantially revised deck until you have explicitly confirmed the outline with the user.**

Before writing any new slide content, you MUST:
1. Present a proposed outline (section titles + slide count + estimated time)
2. Ask: "Does this structure work for you? Let me know if you'd like any changes."
3. Wait for explicit approval before proceeding.

Skipping this step is not allowed for new outlines or major restructures.

## 1. Discovery & Brainstorming

Even when the request appears detailed, **do not start writing slides immediately**. First, clarify open questions, then present the outline for approval.

If the topic or core message is unclear, initiate brainstorming:

1. **Define the Audience**: Who is the target audience? (e.g., junior engineers, executives)
2. **Extract the Core Message**: Distill the most important takeaway into one sentence. Ask: *"What is the one thing you want the audience to remember?"*
3. **Reverse-Engineer the Structure**: Build backwards from the conclusion. Ask: *"What context, evidence, and steps does the audience need to understand this message?"*

## 2. Planning & Scope

Always ask for the allotted presentation time and the target output format (HTML preview only, PDF, PPTX, or both) to determine scope.

**Output rule**: If PDF/PPTX is a target, plan for a fixed slide canvas. Do not rely on scrollable panels, clipped regions, or hover-only details.

**Rule of Thumb**: Use **1 minute per slide** as the default, then let a domain-specific skill override that when its topic normally needs more or less time.

**Template Types**:
- **LT (5-10 mins)**: Conclusion-first approach. Focus on 1 point. (5-10 slides)
- **Standard (20-60 mins)**: Background → Problem → Solution → Evidence → Summary
- **Tutorial (30+ mins)**: Slower pace with step-by-step instructions

**Action**: Explicitly propose target slide count and high-level outline for approval before drafting.

**Visual Check Confirmation**: Always ask if the user wants to perform AI visual layout checks (using vision models) or stay with text-based linting. Explain that visual checks provide higher quality but incur higher token costs.


## 3. Structural Best Practices

When drafting content, apply these rules:

- **1 Slide = 1 Message**: Never overload a slide. Each slide conveys one key point. If multiple major points exist, split it.
- **MECE Principle**: Ensure structure is Mutually Exclusive and Collectively Exhaustive. Seamless flow with no gaps or repetition.
- **Storyline/Flow**: Clear narrative arc: Hook → Problem → Solution → Evidence → Call to Action

## 4. Visual & Design Principles

Keep these in mind when drafting text to ensure content *can* be designed well later:

- **Visual Order**: Plan for neatly aligned content. Keep lists symmetrical.
- **White Space**: Treat white space as active. Use concise bullet points, not paragraphs.
- **Minimize Text**: People cannot read dense slides and listen simultaneously. Reduce to keywords or short phrases.
- **Suggest Visuals**: Explicitly suggest where images, diagrams, charts, or icons would be better than text (e.g., *[Insert Diagram Here]*).

## 5. Workflow Execution

1. **Ask & Clarify**: Time limit? Audience? Core message? Output format?
2. **Brainstorm (if needed)**: Help user find core message
3. **Outline**: Propose section-by-section outline with slide titles and estimated slide count.
4. **Visual Check Opt-in**: Ask: *"Would you like to perform visual layout checks using AI vision later? (High quality, but higher token cost) or stick to text-based linting?"*
5. **WAIT for approval**: Present outline and ask for confirmation — **do not proceed without an explicit OK**
6. **Draft (outline-level only)**: After outline is approved, write slide-level bullet points using placeholders like `[Insert diagram here]` or `[List 3 key benefits]` — **do not write final prose or Marp Markdown yet**
7. **Hand off to `marp-slide-creator`**: Once slide-level content is confirmed, activate `marp-slide-creator` to generate the final Marp Markdown

> **Placeholder rule**: Keep each slide entry at outline-level (title + 2–4 bullet points max) until the user explicitly approves the full structure. Expanding into full text before approval wastes tokens and makes restructuring costly.
