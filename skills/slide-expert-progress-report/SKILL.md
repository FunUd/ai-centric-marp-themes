---
name: slide-expert-progress-report
description: Activate this skill ONLY when creating or editing progress reports or achievement presentation slides.
---

# Progress Report & Achievement Presentation Expert

## Core Philosophy

Progress reports succeed when stakeholders can confidently say: **"This project is on track."**

Purpose: Sharing past results is not the goal—**agreement on the future** is.

## The 5 Essential Components

Every progress report must answer these 5 questions:

| # | Question | Component |
|---|----------|-----------|
| 1 | Is everything on track? | **Overall Status (Traffic Light)** |
| 2 | What progressed this period? | **Current Period Achievements** |
| 3 | What happens next? | **Next Period Plan** |
| 4 | Are there any problems? | **Risks, Issues, Blockers** |
| 5 | What decisions are needed? | **Decision Items / Discussion Points** |

**Critical Rule**: Use **top-down structure** (Executive Summary → Details → Actions).

## Slide Structure Templates

### Template A: Weekly Progress Report (5-7 slides)

1. **Cover**: Title, date, presenter
2. **Overall Status**: Traffic light summary (🟢🟡🔴)
3. **This Week's Achievements**: Milestone progress with plan vs. actual
4. **Next Week's Plan**: Tasks + recovery plan (if delayed)
5. **Risks & Issues**: Current and potential problems
6. **Discussion Items**: Decisions needed from stakeholders

### Template B: Monthly Review (8-10 slides)

1. **Cover**
2. **Executive Summary**: One-slide overview
3. **Milestone Progress**: Gantt or milestone chart
4. **Key Achievements**: 3 major wins this month
5. **Quality Metrics**: Test coverage, bugs, performance
6. **Resource & Cost Status**: Budget burn rate
7. **Next Month Plan**: Major deliverables
8. **Risks & Mitigations**: Top 3 risks
9. **Action Items**: Decision requests

### Template C: Achievement Presentation (Final Delivery)

1. **Cover**
2. **Project Goals Recap**: What we set out to do
3. **Final Deliverables**: What was achieved
4. **Key Metrics**: Performance vs. targets
5. **Challenges & Solutions**: Problems overcome
6. **Lessons Learned**: Insights for future projects

## Component Details

### 1. Overall Status (Traffic Light)

**Structure**:
- **Overall Status**: 🟢 (on track) / 🟡 (caution) / 🔴 (action required)
- **4-Axis Breakdown**: Schedule / Quality / Cost / Resources

**Quantitative Criteria Example**:
- 🟢 Green: Within 1 week variance
- 🟡 Yellow: 1-2 weeks delay
- 🔴 Red: 2+ weeks delay or critical blocker

### 2. Current Period Achievements

**Key Principle**: Express progress as **"Progress against Milestones"** not task lists.

**Format**:
```
Milestone 1: API Development
├─ Task 1: Design review ✅
├─ Task 2: Implementation ✅
└─ Task 3: Unit testing 🔄 (80%)
→ Milestone Progress: 75%
```

**Plan vs. Actual**: Always show variance
- "Planned: 60% → Actual: 55% (5-point delay)"

### 3. Next Period Plan

**Critical Rule**: For delays, always include a **Recovery Plan**.

**Format**:
1. **Next Week's Tasks** (prioritized)
2. **Owner & Due Date** per task
3. **Recovery Plan** (if delayed)

**Recovery Plan Examples**:
- "Compress development phase by 1 week"
- "Add 2 resources for parallel work"
- "Descope non-critical features (list specific items)"

### 4. Risks, Issues, Blockers

**Important Distinction**:
- **Issue**: Problem occurring NOW
- **Risk**: Problem that MIGHT occur

**Format per Item**:
| Field | Description |
|-------|-------------|
| Description | What is the problem |
| Impact Level | High / Medium / Low |
| Status | Identified / Analyzing / Mitigating / Resolved |
| Response Plan | Specific actions |
| Deadline | By when must this be resolved |

**Zero Issues Protocol**: Even if no issues, write: **"No critical issues at this time."**

### 5. Decision Items / Discussion Points

**Format** (Background → Options → Recommendation → Decision Request):
```
[Background]
Current challenge description

[Options]
A) Option A — Pros/cons
B) Option B — Pros/cons

[Recommendation]
Option X — Rationale

[Decision Request]
Please approve [specific action] by [date]
```

## Content Guidelines

### One Slide, One Message

- ❌ Bad: "This Week's Progress, Issues, and Next Steps"
- ✅ Good: "API Integration 75% Complete — On Track"

### Quantify Everything

- ❌ Bad: "Significant progress made"
- ✅ Good: "Milestone 2 at 75% (target: 70%)"

### Lead with Conclusion

- ❌ Bad: "We worked on A, then B, then C, resulting in 80% completion"
- ✅ Good: **"Milestone complete at 80%"** — We delivered A, B, and C

### Visual Over Text

Convert text to visual elements:
- Numbers → Charts or tables
- Status lists → Traffic light matrix
- Sequences → Timeline
- Comparisons → Side-by-side columns

## Visualization Best Practices

| Type | Use When |
|------|----------|
| **Traffic Light** | Overall status at-a-glance |
| **Progress Bar** | Single metric completion |
| **Gantt/Timeline** | Schedule visualization |
| **Plan vs. Actual** | Variance analysis |

### Color Coding Standards

| Color | Meaning | Usage |
|-------|---------|-------|
| 🟢 Green | On track / Complete | Status indicators |
| 🟡 Yellow | Caution / At risk | Warning states |
| 🔴 Red | Critical / Blocked | Action required |
| 🔵 Blue | Information / Plan | Baseline/reference |

## Quality Checklist

Content:
- [ ] Overall status appears on slide 1 or 2
- [ ] Every metric includes baseline for comparison
- [ ] Delays include recovery plans
- [ ] Issues and risks are clearly distinguished
- [ ] Decision items include specific options
- [ ] Next period plan has specific owners and dates

Visual:
- [ ] Traffic light colors used consistently
- [ ] Charts have clear titles and axes
- [ ] Tables fit within slide boundaries
- [ ] Text is scannable (bullet points, not paragraphs)
- [ ] No slide exceeds 6-7 key points

Communication:
- [ ] Report answers "So what?" for each slide
- [ ] Stakeholder can make decisions without clarifying questions
- [ ] Future orientation is clear (not just past reporting)

## The 5 Pillars Summary

1. **Signal First** — Traffic light status upfront
2. **Milestone Focus** — Progress against goals, not task lists
3. **Future Commitment** — Clear next steps with owners
4. **Transparent Issues** — Risks and blockers visible
5. **Action Orientation** — Specific decisions requested


## Workflow Handoff

Once the content structure and text are finalized based on these guidelines, **DO NOT generate the final Marp Markdown directly from this skill**.
Instead, hand off the implementation to the `marp-slide-creator` skill to ensure proper Marp syntax, layout, and overflow prevention.
