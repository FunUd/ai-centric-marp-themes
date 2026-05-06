---
name: slide-expert-postmortem
description: Activate this skill ONLY when PLANNING or OUTLINING Postmortem presentation slides. DO NOT activate during Marp implementation, layout fixing, or exporting.
---

# Postmortem Slide Expert

A specialized skill for creating incident postmortem presentation slides based on Site Reliability Engineering (SRE) best practices and blameless postmortem culture.


## MANDATORY: Confirm Before Drafting

**DO NOT generate any slide content for a new or substantially revised deck until you have explicitly confirmed the outline with the user.**

Before writing any new slide content, you MUST:
1. Present a proposed outline (section titles + slide count + estimated time) based on the guidelines below.
2. Ask: "Does this structure work for you? Let me know if you'd like any changes."
3. Wait for explicit approval before proceeding.

## When to Use This Skill

Use this skill when:
- Documenting and sharing learnings from system outages or incidents
- Creating slides for postmortem review meetings with engineering teams
- Analyzing root causes and defining preventive actions
- Promoting a blameless culture while improving system reliability

## Postmortem Culture Fundamentals

### Purpose of Postmortem Slides

1. **Knowledge Sharing**: Document what happened for organizational learning
2. **System Improvement**: Identify weaknesses and implement preventive measures
3. **Culture Building**: Reinforce blameless culture and psychological safety

### Core Principles (Google SRE Inspired)

- **Blameless Culture**: Focus on system failures, not individual mistakes
- **Learning Opportunity**: Writing a postmortem is a chance to make the system more resilient
- **Actionable Outcomes**: Every postmortem must result in concrete action items with owners
- **Transparency**: Share findings broadly to prevent similar incidents across teams

### Key Elements to Cover

- **Executive Summary**: What happened, impact, and resolution
- **Timeline**: Precise chronological record of the incident
- **Impact Assessment**: User-facing and internal effects
- **Root Cause Analysis**: Contributing factors and trigger
- **Resolution Steps**: How the incident was mitigated
- **Lessons Learned**: What went well, what went wrong, where we got lucky
- **Action Items**: Specific, trackable preventive measures

## Recommended Slide Structure

For the detailed section-by-section slide structure, **please read `references/structure-template.md`**.

## Content Best Practices

### Writing Guidelines

1. **Factual & Data-Driven**: Use metrics, timestamps, and concrete numbers
2. **Blameless Language**: Avoid words like "careless," "negligent," "should have"
3. **System-Focused**: Frame issues as system/process failures, not personal failures
4. **Specific & Actionable**: Vague terms like "improve" or "make better" are insufficient
5. **Complete Timeline**: Include both successful and failed response attempts
6. **Honest Assessment**: Acknowledge what you don't know and where you got lucky

### Blameless Language Examples

| ❌ Avoid | ✅ Use Instead |
|---------|--------------|
| "Engineer X forgot to..." | "The deployment process didn't verify..." |
| "Careless mistake" | "The system allowed an unsafe operation" |
| "Human error" | "The interface didn't prevent invalid input" |
| "They should have checked" | "The checklist didn't include this step" |

### Timeline Best Practices

**Essential Elements to Include**:
- Time incident started (first error, not first alert)
- When monitoring detected the issue
- When on-call was paged
- Key investigation milestones
- Mitigation attempts (successful and failed)
- Resolution time
- Post-incident verification

**Format Example**:
| Time (JST) | Event | Actor |
|------------|-------|-------|
| 14:32:15 | First error logged in service X | System |
| 14:35:00 | PagerDuty alert triggered | Monitoring |
| 14:38:00 | On-call engineer acknowledged | @sato |
| 14:45:00 | Mitigation: Rolled back deployment | @sato |
| 15:15:00 | Service fully recovered | System |

### Root Cause Analysis Techniques

**5 Whys Example**:
1. Why did the database fail? → Connection pool exhausted
2. Why was the pool exhausted? → New feature increased connection duration
3. Why wasn't this caught in testing? → Load testing didn't simulate realistic patterns
4. Why weren't realistic patterns tested? → Test data didn't reflect production query mix
5. Why was test data insufficient? → No process for syncing production query patterns to tests

**Root Cause: Missing process for keeping test data representative of production**

### Action Item Categories

| Type | Purpose | Example |
|------|---------|---------|
| **Prevent** | Stop incident from recurring | Add circuit breaker to prevent cascading failure |
| **Detect** | Find issues earlier | Add alert for connection pool saturation |
| **Mitigate** | Reduce impact if it happens again | Implement automatic rollback on error rate spike |
| **Process** | Improve response procedures | Update runbook with steps for this scenario |

### Action Item Quality Standards

- **Specific**: "Add connection timeout of 5s to API client"
- **Measurable**: Success criteria is clear
- **Assigned**: One owner (can delegate, but one person accountable)
- **Prioritized**: P0 (immediate), P1 (this quarter), P2 (backlog)
- **Tracked**: Linked to a bug/ticket for follow-up

## Quality Checklist

- [ ] Timeline is complete and accurate (verified with logs)
- [ ] Root cause is traced to system/process issues, not individuals
- [ ] Impact is quantified with specific metrics
- [ ] All contributing factors are identified
- [ ] Action items are specific, assigned, and trackable
- [ ] Language is blameless and factual
- [ ] What went well is acknowledged (not just problems)
- [ ] Where we got lucky is documented
- [ ] Reviewers can understand the incident without prior context


## Workflow Handoff

Once the content structure and text are finalized based on these guidelines, **DO NOT generate the final Marp Markdown directly from this skill**.
Instead, hand off the implementation to the `marp-slide-creator` skill to ensure proper Marp syntax, layout, and overflow prevention.

> **Diagram Warning for Implementation Phase:** When suggesting diagrams (like Sequence or Flowcharts), remind the user that inline Mermaid (` ```mermaid `) fails in Marp PDF exports. Diagrams must be placed as placeholder images (`![Diagram](./assets/diagram.svg)`) and generated offline using Mermaid CLI during the implementation phase.

