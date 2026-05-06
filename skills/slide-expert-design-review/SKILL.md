---
name: slide-expert-design-review
description: Activate this skill ONLY when creating or editing design review presentation slides.
---

# Design Review Slide Expert

A specialized skill for creating technical design review presentation slides based on software design documentation best practices and established design review methodologies.

## When to Use This Skill

Use this skill when:
- Creating slides to explain system/module design to stakeholders
- Preparing for technical design review meetings
- Need to cover architecture, interfaces, state transitions, or exception handling
- Seeking approval/consensus on design decisions

## Design Review Fundamentals

### Purpose of Design Review Slides

1. **Quality Improvement**: Identify defects and inconsistencies before implementation
2. **Alignment**: Ensure all stakeholders share the same understanding of the design
3. **Knowledge Sharing**: Distribute design knowledge across the team

### Key Elements to Cover

- **Introduction & Overview**: Goals, scope, and requirements
- **System Architecture**: High-level structure and component relationships
- **Data Design**: Data flow, storage, and validation rules
- **Interface Design**: API specifications, protocols, error handling
- **Component Design**: Module responsibilities, inputs/outputs, algorithms
- **State Transitions**: State diagrams and transition conditions
- **Exception Handling**: Error scenarios and recovery procedures

### Design Review Checklist (5 Key Perspectives)

Ensure your slides address these review perspectives:
1. **Completeness**: No omissions in requirements (functional + non-functional)
2. **Clarity**: No ambiguous expressions or unclear specifications
3. **Consistency**: No contradictions within the design
4. **Feasibility**: Technically implementable within constraints
5. **Usability**: User-friendly design considering actual usage scenarios

## Recommended Slide Structure

For the detailed section-by-section slide structure, **please read `references/structure-template.md`**.

## Content Best Practices

### Writing Guidelines

1. **Use Templates**: Follow consistent formatting for each section type
2. **Visual First**: Use diagrams, flowcharts, and tables instead of paragraphs
   - Architecture diagrams for system structure
   - Sequence diagrams for interface flows
   - State machine diagrams for state transitions
   - Tables for API specifications
3. **Single Document**: Cover the complete design in one presentation
4. **Explicit Open Items**: Clearly mark unresolved issues
5. **Avoid Ambiguity**: Remove vague expressions ("etc.", "appropriate", "as needed")
6. **Self-Check**: Review your own slides before presenting

### Slide Content Guidelines

| Element | Recommended Approach |
|---------|---------------------|
| Architecture | Use component diagrams with clear boundaries |
| Interfaces | Present API specs in table format (method, params, response) |
| State Transitions | Use state machine diagrams with transition labels |
| Exceptions | Categorize by severity and show handling flow |
| Decisions | Include "Why" alongside "What" for key choices |

## Exception Handling Deep Dive

Design reviews often overlook exception handling. Ensure your slides cover:

**Normal Flow vs Exception Flow**:
- Show the happy path clearly
- Identify all deviation points
- Document recovery for each exception

**Exception Categories**:
1. **System Exceptions**: Network errors, DB failures, resource exhaustion
2. **Business Exceptions**: Invalid state transitions, business rule violations
3. **Validation Exceptions**: Input format errors, missing required fields
4. **Security Exceptions**: Auth failures, permission denials

**Documentation Format**:
| Scenario | Trigger | System Response | User Message |
|----------|---------|-----------------|--------------|
| DB timeout | Query > 30s | Retry 3x, then fail | "Service temporarily unavailable" |

## State Transition Documentation

For complex state machines, document:
- **All States**: With clear definitions of what each means
- **All Events**: That can trigger transitions
- **Guards**: Conditions that must be met for a transition
- **Actions**: What happens during transitions
- **Entry/Exit**: Actions on entering/exiting states

## Quality Checklist

- [ ] All functional requirements are covered
- [ ] Normal flow and exception flows are both documented
- [ ] Non-functional requirements (performance, security) addressed
- [ ] Interface specifications are complete (request/response/error)
- [ ] State transitions cover all possible paths
- [ ] Error handling includes recovery procedures
- [ ] Open questions are clearly identified
- [ ] No ambiguous or unclear expressions
- [ ] No contradictions within the design


## Workflow Handoff

Once the content structure and text are finalized based on these guidelines, **DO NOT generate the final Marp Markdown directly from this skill**.
Instead, hand off the implementation to the `marp-slide-creator` skill to ensure proper Marp syntax, layout, and overflow prevention.
