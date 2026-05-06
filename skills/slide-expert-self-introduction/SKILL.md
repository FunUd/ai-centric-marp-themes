---
name: slide-expert-self-introduction
description: Activate this skill ONLY when creating or editing self-introduction presentation slides.
---

# Self-Introduction Slide Expert

This skill provides guidelines for creating impactful self-introduction slides for engineers joining new teams, being assigned as mentors, or transferring departments.

## Basic Principles

The core purpose of a self-introduction slide is to **spark conversation and build connections**. Keep these principles in mind:

- **Brevity is key**: 1 slide ideally, maximum 3 slides
- **Balance professional and personal**: Mix work background with personal interests
- **Create conversation hooks**: Include topics others can ask about
- **Be authentic**: Share genuine interests, not what you think others want to hear

## Recommended Slide Structure

For the detailed section-by-section slide structure, **please read `references/structure-template.md`**.

## Design Best Practices

### Visual Hierarchy

1. **Photo placement**: Top-left or center; should be prominent but not dominate
2. **Name**: Largest text on the slide (H1 level)
3. **Role/Title**: Secondary emphasis (H2 level)
4. **Supporting info**: Smaller, grouped logically

### Content Guidelines

**DO:**
- Use bullet points sparingly; prefer short phrases
- Include icons for visual interest (tech stack, hobbies)
- Keep text aligned and consistently formatted
- Use color sparingly to highlight key info only

**DON'T:**
- List every technology you've ever touched
- Include age, marital status, or other potentially sensitive personal details unless you choose to
- Use overly formal language that doesn't sound like you
- Create dense slides that read like a resume

### Photo Tips

- Use a recent photo where your face is clearly visible
- Plain or simple background works best
- Expression: friendly smile, approachable
- Crop to head-and-shoulders or square format
- Ensure image quality is high (not pixelated)

## Content Writing Tips

### The "Hook" Section

This is the most important part for building connections. Good hooks include:

- **Hobbies**: "Weekend hiker" / "Board game collector" / "Homebrew coffee enthusiast"
- **Recent learning**: "Currently learning Rust" / "Studying for AWS certification"
- **Fun facts**: "I've visited 15 countries" / "I can solve a Rubik's cube in under 2 minutes"
- **Team-related**: "Excited to work with this team because..."

### Technical Skills Presentation

Instead of listing: "JavaScript, TypeScript, React, Node.js, Python, Docker, Kubernetes..."

Try grouping:
- **Frontend**: React, TypeScript, Next.js
- **Backend**: Node.js, Python, Go
- **DevOps**: Docker, Kubernetes, AWS

Or use proficiency levels:
- **Daily use**: React, TypeScript
- **Experienced**: Python, AWS
- **Exploring**: Rust, WebAssembly

### Background Summary

Keep career history to 2-3 lines max. Examples:

> "Previously at [Company] building microservices for fintech. Before that, frontend lead at a startup. Started career in QA, which taught me the value of testing."

> "New grad from [University] Computer Science. 2 internships in mobile development. Joining as my first full-time role—excited to learn from everyone!"

## Quick Checklist

Before finalizing your self-introduction slide, verify:

- [ ] All information is current and accurate
- [ ] No typos in names, technologies, or contact info
- [ ] Photo is clear and professional
- [ ] Text is readable at a distance (test by zooming out)
- [ ] Includes at least one personal/conversational element
- [ ] Fits within 1-3 slides maximum
- [ ] Contact information is appropriate for sharing

## Example Content Structures

### Example 1: Experienced Engineer

```
Name: Yuki Tanaka
Role: Senior Backend Engineer

Background:
- 5 years at FinTech Corp building payment APIs
- Led team of 4 engineers for 2 years
- Open source contributor (Redis client libs)

Skills: Go, Python, PostgreSQL, Kubernetes, AWS

Hook: "Marathon runner—currently training for Tokyo Marathon 2026"
```

### Example 2: New Graduate

```
Name: Kenji Sato
Role: Frontend Engineer (New Grad)

Background:
- CS degree from Tokyo University
- 2 internships: mobile dev and web accessibility
- Personal project: Indie game with 10K downloads

Skills: React, TypeScript, Flutter, Figma

Hook: "Retro game collector—own 50+ classic consoles"
```

### Example 3: Transfer/Mentor Assignment

```
Name: Mei Yamamoto
Role: Engineering Manager (Mentor)

Background:
- 8 years in SaaS industry
- Previously led Growth Team (joined as 5th engineer)
- Passionate about onboarding and documentation

Skills: Ruby, Rails, Team Building, Technical Writing

Hook: "Weekend potter—love creating functional ceramics"
```

## Common Mistakes to Avoid

1. **Resume-style slides**: Don't copy-paste your CV
2. **Too much humility**: It's OK to highlight achievements
3. **No personal element**: Purely professional introductions are forgettable
4. **Over-designing**: Fancy animations or excessive styling distract
5. **Information overload**: List 20 technologies you've touched once
6. **Generic statements**: "I like coding" vs. "I love optimizing database queries"

## Success Criteria

A successful self-introduction slide results in:
- Colleagues remembering your name and role
- At least one person asking about your "hook" content
- Follow-up conversations in the following days
- People feeling comfortable approaching you

Remember: **The goal is connection, not perfection.**


## Workflow Handoff

Once the content structure and text are finalized based on these guidelines, **DO NOT generate the final Marp Markdown directly from this skill**.
Instead, hand off the implementation to the `marp-slide-creator` skill to ensure proper Marp syntax, layout, and overflow prevention.
