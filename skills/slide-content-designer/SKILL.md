---
name: slide-content-designer
description: Activate this skill at the START of a new presentation project, before any slides are written. Use when the user wants to plan, outline, or structure a presentation — defining the audience, core message, slide count, and section flow. This skill covers the content design phase only. Once the outline is approved, hand off to marp-slide-creator for Markdown implementation.
---

# Slide Content Designer

This skill provides a structured workflow and established best practices for creating high-quality presentation slides. It focuses heavily on the "planning and structuring" phase, which is often the most time-consuming part of slide creation. 

Use this skill when a user wants to create a presentation, outline a talk, or needs help figuring out what to say in their slides.

> **Note:** This skill focuses on the *content, structure, and general design principles*. For Marp-specific Markdown generation or styling, rely on the `marp-slide-creator` skill after the content outline is finalized.

## MANDATORY: Always Confirm Before Writing

**DO NOT generate any slides until you have explicitly confirmed the outline with the user.**
This rule applies even when the topic, structure, and content seem clear from the user's request.

Before writing any slide content, you MUST:
1. Present a proposed outline (section titles + slide count per section + estimated time per section)
2. Ask the user: "Does this structure work for you? Let me know if you'd like any changes." (or equivalent in the user's language)
3. Wait for explicit approval before proceeding.

Skipping this step — for any reason, including a seemingly detailed request — is not allowed.

## 1. Discovery & Brainstorming

Even when the user's request appears detailed, **do not start writing slides immediately**. First, clarify any open questions, then present the outline for approval (see MANDATORY section above).

If the topic or core message is genuinely unclear, initiate a brainstorming session:

1.  **Define the Audience:** Ask the user who the target audience is (e.g., junior engineers, tech leads, business executives).
2.  **Extract the Core Message:** Work with the user to distill the absolute most important takeaway into a single, concise sentence. Ask: *"What is the one thing you want the audience to remember after this talk?"*
3.  **Reverse-Engineer the Structure:** Once the core message (the conclusion) is defined, build the structure backwards. Ask yourself and the user: *"What background context, evidence, and logical steps does the audience need to understand and agree with this core message?"*

## 2. Planning & Scope

Always ask for the allotted presentation time to determine the scope. 

*   **Rule of Thumb:** Calculate slide count based on **1 minute per slide** (e.g., a 20-minute presentation should be around 15–20 slides).
*   **Template Types based on Time:**
    *   **LT (Lightning Talk, 5-10 mins):** Use a "Conclusion First" approach. Focus on 1 point. (5-10 slides)
    *   **Standard (20-60 mins):** Background -> Problem -> Solution -> Demo/Evidence -> Summary.
    *   **Tutorial/Hands-on (30+ mins):** Slower pace, includes step-by-step instructions and verification steps.

*Action:* Explicitly propose the target number of slides and the high-level outline to the user for approval before drafting.

## 3. Structural Best Practices

When drafting the actual slide content, rigorously apply these rules:

*   **1 Slide = 1 Message:** Never overload a slide. Each slide should convey one and only one key point. If a slide has multiple major points, split it.
*   **MECE Principle:** Ensure the content structure is Mutually Exclusive and Collectively Exhaustive. The logical flow should be seamless, with no gaps in the argument and no unnecessary repetition.
*   **Storyline/Flow:** Ensure there is a clear narrative arc: Hook -> Problem -> Solution -> Evidence -> Call to Action/Conclusion.

## 4. Visual & Design Principles (Agnostic)

Even when just drafting text, keep these visual design principles in mind to ensure the content *can* be designed well later:

*   **Visual Order:** Plan for content that can be neatly aligned. Keep lists symmetrical where possible.
*   **White Space:** Treat white space as an active element. Do not write paragraphs of text; use concise bullet points. Provide enough breathing room so the audience isn't overwhelmed.
*   **Minimize Text:** People cannot read a dense slide and listen to the speaker at the same time. Reduce full sentences to keywords or short phrases.
*   **Suggest Visuals:** When drafting text, explicitly suggest where an image, diagram, chart, or icon would be better than text (e.g., *[Insert Architectural Diagram Here]*).

## 5. Workflow Execution

1.  **Ask & Clarify:** Time limit? Audience? Core message?
2.  **Brainstorm (if needed):** Help the user find their core message.
3.  **Outline:** Propose a section-by-section outline and slide count based on the time limit.
4.  **WAIT for approval:** Present the outline and explicitly ask for confirmation. Do not proceed until the user approves.
5.  **Draft:** Generate the slide text applying "1 Slide = 1 Message" and MECE.
