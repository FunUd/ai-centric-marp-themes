---
name: slide-expert-tech-sharing
description: ALWAYS activate this skill when creating or editing study group or technical sharing presentation slides. Specialized skill for engineers sharing knowledge, best practices, case studies, or technical insights with teams and organizations. Use whenever the user mentions 勉強会, tech talk, knowledge sharing, or wants to structure slides for technical knowledge transfer with audience analysis, storytelling, and visual design patterns.
---

# Technical Sharing Slide Expert

A guide for creating effective technical sharing and study group presentation slides for engineers.

## Understanding Your Audience

### Audience Analysis Framework

Before creating slides, analyze your audience:

| Dimension | Questions to Ask | Impact on Content |
|-----------|-----------------|-------------------|
| **Technical Level** | Beginner/Intermediate/Expert? | Determines depth of explanation needed |
| **Domain Knowledge** | Familiar with the topic area? | Affects prerequisite explanations |
| **Role Diversity** | Developers/PMs/Managers? | Balances technical vs business value |
| **Learning Goals** | What should they take away? | Shapes the core message and structure |
| **Time Context** | Lunch session/Full workshop? | Determines content volume (1 slide ≈ 2 min) |

### Content Calibration Guidelines

- **Mixed Audience**: Start with fundamentals, provide advanced details in appendices
- **Same-Team Sharing**: Skip basics, dive into implementation details and lessons learned
- **Cross-Team Sharing**: Emphasize applicability and integration points
- **Management Present**: Include business impact and resource trade-offs

## Content Structure & Storytelling

### Recommended Slide Structure

| Section | Purpose | Typical Slide Count |
|---------|---------|---------------------|
| **Cover** | Title, presenter, date | 1 |
| **Hook** | Why should audience care? | 1 |
| **Agenda** | What will be covered | 1 |
| **Background** | Context and problem statement | 1-2 |
| **Core Content** | Main technical explanation | 40% of slides |
| **Case Study** | Real implementation example | 2-3 |
| **Best Practices** | Lessons learned, recommendations | 1-2 |
| **Summary** | Key takeaways | 1 |
| **Q&A/Next Steps** | Discussion and follow-up | 1 |

### The "1 Slide = 1 Message" Rule

Each slide should convey exactly one clear message:

- **❌ Bad**: "Overview of our architecture, performance metrics, and future plans"
- **✅ Good**: "Microservices architecture reduced deployment time by 60%"

### Storytelling Techniques

**The Problem-Solution-Impact Pattern:**
```
We faced [specific challenge] → 
We tried [approach/technology] → 
Result was [measurable outcome] → 
Key lesson: [actionable insight]
```

**The Before-After Comparison:**
- Visual side-by-side comparison of old vs new approach
- Concrete metrics (performance, maintainability, cost)
- Clear explanation of trade-offs

## Slide Design Principles

### Timing Guidelines

- **Standard pace**: 1 slide = 2 minutes
- **Code-heavy slides**: 1 slide = 3-4 minutes
- **Interactive/demo slides**: 1 slide = 5+ minutes

| Duration | Total Slides | Notes |
|----------|--------------|-------|
| 15 min | 7-8 slides | Lunch session, focused topic |
| 30 min | 14-16 slides | Standard tech talk |
| 60 min | 25-30 slides | Workshop with demos |

### Content Density Rules

- **Maximum bullet points**: 5 per slide
- **Maximum list items**: 7 (magic number rule)
- **Code lines per slide**: 10-15 maximum
- **Text density**: < 60% of slide area

### Visual Hierarchy

1. **Title**: Clear, specific (not generic like "Overview")
2. **Key Visual**: Diagram, code snippet, or chart
3. **Supporting Text**: Minimal, bullet points
4. **Callout Boxes**: Highlight important insights or warnings

## Technical Content Patterns

### Code Presentation Best Practices

**Good Code Slide Structure:**
- Focus on the essential logic
- Remove boilerplate and error handling
- Use comments to explain WHY, not WHAT
- Show incremental improvement (v1 → v2 → v3)
- Include performance annotations (time/space complexity)

### Architecture Diagram Guidelines

- **Layered View**: Show components and their relationships
- **Data Flow**: Use arrows to indicate direction of data movement
- **Color Coding**: Consistent colors for service types (e.g., blue=data, green=compute)
- **Annotations**: Add brief explanations for key decisions

### Metrics and Performance Data

**Presentation Tips:**
- Use relative improvements ("2x faster") over absolute numbers
- Include baseline for context
- Visualize with simple charts (bar > line > table)
- Show confidence intervals or sample sizes when relevant

### Technology Comparison Slides

**Effective Comparison Structure:**

| Aspect | Option A | Option B |
|--------|----------|----------|
| **Pros** | Specific advantages | Specific advantages |
| **Cons** | Clear limitations | Clear limitations |
| **Best For** | Use case description | Use case description |

## Case Study Presentation

### Case Study Slide Structure

A compelling case study follows this narrative:

1. **Situation**: What was the context and challenge?
2. **Approach**: What solution did you implement?
3. **Results**: What were the measurable outcomes?
4. **Lessons**: What would you do differently?

### Before/After Comparison Template

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Response time | 2.5s | 0.8s | **-68%** |
| Error rate | 5% | 0.5% | **-90%** |
| Infrastructure cost | $X/month | $0.7X/month | **-30%** |
| Maintenance | 20 hrs/week | 5 hrs/week | **-75%** |

### Lessons Learned Format

Structure insights using this pattern:
- **What we tried**: Brief description of the approach
- **What happened**: Outcome (success or failure)
- **Key insight**: Actionable takeaway for the audience

## Q&A and Discussion

### Preparation for Discussion

**Prepare backup slides for likely questions:**
- Alternative approaches you considered
- Detailed implementation notes
- Performance benchmarks with more context
- Security/privacy considerations

### Discussion Facilitation

**Questions to seed discussion:**
- "Has anyone faced a similar challenge in their team?"
- "What alternative approaches have you considered?"
- "How would you adapt this for [different context]?"

### Follow-up Resources Slide

Include a slide with:
- Links to documentation/tools mentioned
- Repository/code samples (if shareable)
- Related reading or further learning resources
- Contact information for follow-up questions

## Preparation Checklist

### Before Creating Slides

- [ ] Defined the single core message I want to convey
- [ ] Analyzed audience technical level and interests
- [ ] Determined appropriate slide count based on time
- [ ] Gathered supporting data, code examples, and visuals

### Content Review

- [ ] Each slide has exactly one clear message
- [ ] Technical jargon is defined or replaced with accessible language
- [ ] Code examples are minimal and commented for "why" not "what"
- [ ] Numbers/metrics include context (baseline, sample size)
- [ ] Case studies include both successes AND failures/lessons

### Design Review

- [ ] Slides follow 1 slide ≈ 2 minutes guideline
- [ ] No slide has more than 5 bullet points
- [ ] Visual hierarchy is clear (title → key visual → supporting text)
- [ ] Color scheme is consistent and accessible
- [ ] Code is syntax highlighted and properly sized (16-18px)
