---
name: slide-expert-release-notes
description: Activate this skill ONLY when PLANNING or OUTLINING Release Notes presentation slides. DO NOT activate during Marp implementation, layout fixing, or exporting.
---

# Release Notes & Change Communication Slide Skill


## MANDATORY: Confirm Before Drafting

**DO NOT generate any slide content for a new or substantially revised deck until you have explicitly confirmed the outline with the user.**

Before writing any new slide content, you MUST:
1. Present a proposed outline (section titles + slide count + estimated time) based on the guidelines below.
2. Ask: "Does this structure work for you? Let me know if you'd like any changes."
3. Wait for explicit approval before proceeding.

## Skill Overview

This skill assists in creating slide materials that effectively communicate release content, impact scope, and important notes to stakeholders.

## Slide Structure Template

### Standard Structure (8-12 slides)

1. **Cover** - Release name, version, and date
2. **Release Overview** - The core value of this release in one sentence
3. **Release Schedule** - Timeline and milestones
4. **Key Changes Highlights** - Up to 3 major changes
5. **New Features Details** - User-centric explanations (split if multiple features)
6. **Improvements & Changes** - Modifications to existing features
7. **Bug Fixes** - Fixed issues and their impact (if applicable)
8. **Impact Scope & Target Users** - Who is affected and how
9. **Important Notes & Breaking Changes** - Migration steps and required actions
10. **Rollout Plan** - For phased releases
11. **FAQ & Common Questions** - Proactive Q&A
12. **Summary & Next Steps** - Action items and contact information

## Section-by-Section Creation Guidelines

### Cover

**Required Elements**:
- Release name/version (e.g., v2.5.0 Spring Release)
- Release date
- Target system/product name
- Author and contact information

**Best Practices**:
- Use semantic versioning (major.minor.patch)
- Consider adding a nickname to make the release memorable (optional)

### Release Overview (Executive Summary)

**Content for 1 slide**:
- The greatest value of this release (1 sentence)
- Target user segments
- Main categories and counts (e.g., 2 new features, 5 improvements, 3 fixes)

**Writing Tips**:
```
❌ "Optimized backend API"
⭕ "Response speed improved by 30%, reducing daily processing time"
```

### Key Changes Highlights

**Structure**:
- Maximum 3 items (more won't be memorable)
- Each item: Icon + Heading (within 20 characters) + 1-line description

**Priority**:
1. Changes with significant user impact
2. Changes with high business value
3. Attention-grabbing new features

### New Features & Improvements Detail Slides

**Structure per feature**:

**What You Can Now Do**:
- Specific user benefit 1
- Specific user benefit 2

**Target Users**: Users of XXX feature  
**How to Use**: Settings → XXX → YYY

**Best Writing Practices**:

- **Headings should be around 20 characters**, concise enough to read at a glance
- **Use the format "You can now do ~~ with ~~"** as the standard
- **Communicate what users can now do and the value they receive**, not just what changed on the screen

```
Before: Added [Update Account Info] button to request list screen
After:  Can now re-retrieve latest employee information from request list screen
```

### Impact Scope & Target Users

**Visualization Method**:

| Target Users | Impact Type | Required Actions |
|--------------|-------------|------------------|
| Admins | Workflow changes | Need to review settings |
| General Users | UI changes | None (auto-applied) |
| API Users | Breaking changes present | Migration guide reference required |

**What to Communicate**:
- Who is affected (user segments)
- What kind of impact (positive/negative)
- Whether action is needed (immediate/planned/none)

### Important Notes & Breaking Changes

**Required Elements**:
- **Changes from previous version**: What will change
- **Migration steps**: Step-by-step instructions
- **Timeline**: When changes become effective
- **Support**: Contact for questions and issues

**Visual Emphasis**:
- Use ⚠️ icons and red color for visual emphasis
- Apply "Action Required" labels where applicable

### FAQ Slide

**Structure Patterns**:

**Pattern A: Common Questions (3-4 Qs)**
```
Q: What happens to existing data?
A: Automatic migration occurs. No manual operation needed.

Q: Is training available?
A: Webinar scheduled for 3/15. Recording will be kept.
```

**Pattern B: Key Concerns (Proactive addressing)**
```
Concerns                    Mitigation
─────────────────────────────────────────
Downtime?           →   Late-night maintenance, impact under 5 min
Legacy data compatibility? →   Automatic migration support ready
Learning curve?     →   1-week transition period + tutorial provided
```

## Slide Creation Best Practices

### One Idea Per Slide

- **1 Slide = 1 Message** principle
- Split into multiple slides if there are multiple takeaways
- Clarify what the audience should remember from each slide

### Category-based Labeling

**Consistent Categorization**:

| Category | Label Color | Icon | Usage |
|----------|-------------|------|-------|
| New Feature | Green | ✨/🚀 | Newly added functionality |
| Improvement | Blue | ⬆️/🔧 | Enhancement to existing features |
| Bug Fix | Purple | 🐛/✅ | Bug fixes |
| Breaking Change | Red/Orange | ⚠️/🚨 | Changes requiring attention |
| Deprecation | Gray | 🗑️ | Features being discontinued |

### Text Minimization

**Character Count Guidelines**:
- Headings: Within 20 characters
- Bullet points: Within 30 characters per line
- Summary slides: aim for roughly 100 characters total; detailed feature or migration slides may be longer when screenshots, tables, or step lists are clearer

**Text Reduction Techniques**:
- Formal Japanese "desu/masu" → Plain form ending with nouns
- Omit periods (headings only)
- Convert to diagrams and bullet points

## Stakeholder-Specific Approaches

### For Executives/Management

**Focus**:
- Business impact (effect on KPIs)
- Risks and countermeasures
- ROI

**Slide Adjustments**:
- Minimize technical details
- Use data and graphs
- Place information needed for approval at the top

### For Product Managers/Developers

**Focus**:
- Detailed feature specifications
- API changes and technical migration procedures
- Known constraints and trade-offs

**Slide Adjustments**:
- Technical terminology acceptable
- Include code examples and API specifications
- Detail breaking changes clearly

### For End Users

**Focus**:
- How to operate and workflow changes
- Visual changes
- Answers to common questions

**Slide Adjustments**:
- Heavy use of screenshots and GIFs
- Step-by-step guides
- Avoid jargon or include explanations

### For Customer Support/CS

**Focus**:
- Inquiry response manuals
- Known issues and workarounds
- Escalation paths

**Slide Adjustments**:
- Prioritize FAQs
- Include troubleshooting guides
- Provide talk script examples

## Tone & Style Guidelines

### User-First Rephrasing

```
❌ "Implemented ~~" (developer perspective)
⭕ "You can now use ~~" (user benefit)

❌ "Optimized API"
⭕ "Response speed increased, reducing processing time"

❌ "Fixed bugs"
⭕ "~~ issues resolved, enabling stable usage"
```

### Specific Expressions

**Avoid** → **Recommended**:
- "Improved" → "Added ~~", "Changed ~~", "Speed up ~~"
- "Prohibited" → "Restricted", "Not available" (for specification controls)
- "Some" → Specific numbers and counts

## Checklist

### Pre-Publication Required Checks

- [ ] **Scannability**: Can the structure be grasped at a glance?
- [ ] **User Value**: Is user benefit stated for each change?
- [ ] **Impact Scope**: Is it clear who is affected and how?
- [ ] **Action**: Are procedures clear when action is needed?
- [ ] **Consistency**: Are notations, formats, and terminology unified?
- [ ] **Visual Assets**: Are screenshots up-to-date and accurate?
- [ ] **Technical Accuracy**: Has it been reviewed by the development team?

### Quality Checks

- [ ] **One Slide One Message**: No mixed themes?
- [ ] **Character Count**: Is the summary slide concise without forcing detail slides into an artificial limit?
- [ ] **Visual Hierarchy**: Is important information emphasized?
- [ ] **Links**: Do links to related materials work?
- [ ] **Dates**: Are release dates and deadlines accurate?


## Workflow Handoff

Once the content structure and text are finalized based on these guidelines, **DO NOT generate the final Marp Markdown directly from this skill**.
Instead, hand off the implementation to the `marp-slide-creator` skill to ensure proper Marp syntax, layout, and overflow prevention.

> **Diagram Warning for Implementation Phase:** When suggesting diagrams (like Sequence or Flowcharts), remind the user that inline Mermaid (` ```mermaid `) fails in Marp PDF exports. Diagrams must be placed as placeholder images (`![Diagram](./assets/diagram.svg)`) and generated offline using Mermaid CLI during the implementation phase.

