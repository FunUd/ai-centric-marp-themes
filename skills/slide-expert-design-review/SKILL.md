---
name: slide-expert-design-review
description: ALWAYS activate this skill when creating or editing design review presentation slides. Specialized skill for creating technical design review slides covering architecture, interfaces, state transitions, and exception handling. Use when the user needs to explain design content (structure/IF/state transitions/exception handling) and obtain review approval. This skill provides structured slide organization based on software design documentation best practices and design review methodologies.
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

### Section 1: Opening (2-3 slides)
- **Cover Slide**: Title, date, presenter, review scope
- **Agenda**: What will be covered in this review
- **Objectives & Goals**: What decisions need to be made today

### Section 2: Background & Context (2-3 slides)
- **Problem Statement**: What problem does this design solve?
- **Requirements Summary**: Key functional and non-functional requirements
- **Constraints**: Technical, business, or timeline constraints

### Section 3: Architecture Overview (3-5 slides)
- **High-Level Architecture**: System diagram showing major components
- **Component Responsibilities**: What each module does
- **Design Decisions**: Why this architecture was chosen (trade-offs)

### Section 4: Interface Design (3-5 slides)
- **External Interfaces**: APIs, protocols, integration points
- **Internal Interfaces**: Module-to-module communication
- **Data Formats**: Request/response structures, message formats
- **Security & Authentication**: How interfaces are secured

### Section 5: State Transitions (2-4 slides)
- **State Diagram**: Visual representation of states and transitions
- **State Descriptions**: What each state represents
- **Transition Conditions**: Events triggering state changes
- **State Actions**: Entry/exit/during actions for each state

### Section 6: Exception Handling (2-4 slides)
- **Error Categories**: System errors, business errors, validation errors
- **Error Scenarios**: Specific cases that can go wrong
- **Recovery Procedures**: How the system handles each error type
- **Error Responses**: User-facing messages and logging

### Section 7: Summary & Next Steps (1-2 slides)
- **Design Summary**: Key points and decisions
- **Open Questions**: Items needing further discussion
- **Action Items**: Who does what by when
- **Approval Request**: Explicit ask for review approval

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
