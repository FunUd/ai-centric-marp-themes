---
name: slide-expert-postmortem
description: ALWAYS activate this skill when creating or editing postmortem/incident report presentation slides. Specialized skill for creating blameless postmortem slides that document incident causes, impact, timeline, and preventive actions. Use when the user needs to share learning from system failures, outages, or incidents with engineering teams. This skill provides structured slide organization based on SRE best practices and postmortem culture.
---

# Postmortem Slide Expert

A specialized skill for creating incident postmortem presentation slides based on Site Reliability Engineering (SRE) best practices and blameless postmortem culture.

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

### Section 1: Opening (2-3 slides)
- **Cover Slide**: Incident name/ID, date, duration, presenter
- **Agenda**: What will be covered in this review
- **Executive Summary**: One-slide overview of what happened and impact

### Section 2: Incident Overview (2-3 slides)
- **Incident Metadata**: ID, severity, duration, detection method
- **Impact Summary**: Affected users/services, error rates, data loss
- **Trigger & Root Cause (High-Level)**: Brief explanation for context

### Section 3: Timeline (2-4 slides)
- **Detailed Timeline**: Chronological breakdown of key events
- **Detection to Resolution**: How the incident unfolded
- **Response Actions**: Who did what and when

### Section 4: Root Cause Analysis (3-5 slides)
- **Contributing Factors**: All elements that led to the incident
- **Trigger Event**: What specifically caused the failure
- **5 Whys Analysis**: Deep dive into underlying causes
- **System Diagram**: Visual representation of failure chain

### Section 5: Impact Assessment (2-3 slides)
- **User Impact**: Downtime, degraded experience, data effects
- **Business Impact**: Revenue, SLA violations, reputation
- **Internal Impact**: Team disruption, on-call burden

### Section 6: Response & Resolution (2-3 slides)
- **Detection**: How the issue was discovered
- **Mitigation Steps**: Immediate actions to reduce impact
- **Resolution**: Permanent fix and verification

### Section 7: Lessons Learned (2-4 slides)
- **What Went Well**: Effective responses, good monitoring, fast mitigation
- **What Went Wrong**: Gaps in process, missing safeguards, slow response
- **Where We Got Lucky**: Near misses, fortunate circumstances

### Section 8: Action Items (1-2 slides)
- **Preventive Actions**: Changes to prevent recurrence
- **Detective Actions**: Improvements to catch issues earlier
- **Mitigative Actions**: Reducing impact if incident recurs
- **Tracking**: Owners, priorities, and due dates

### Section 9: Closing (1 slide)
- **Summary**: Key takeaways
- **Questions**: Open floor for discussion
- **Next Steps**: Follow-up meetings or reviews

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
