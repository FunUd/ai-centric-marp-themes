---
name: slide-expert-api-architecture
description: Activate this skill ONLY when PLANNING or OUTLINING Api Architecture presentation slides. DO NOT activate during Marp implementation, layout fixing, or exporting.
---

# API & System Architecture Explanation Slide Expert

A specialized skill for creating slides that explain API and system architecture, data flows, and component responsibilities based on the C4 model and architecture documentation best practices.


## MANDATORY: Confirm Before Drafting

**DO NOT generate any slide content for a new or substantially revised deck until you have explicitly confirmed the outline with the user.**

Before writing any new slide content, you MUST:
1. Present a proposed outline (section titles + slide count + estimated time) based on the guidelines below.
2. Ask: "Does this structure work for you? Let me know if you'd like any changes."
3. Wait for explicit approval before proceeding.

## When to Use This Skill

Use this skill when:
- Presenting system architecture to stakeholders
- Explaining data flows between system components
- Documenting API interactions and interfaces
- Onboarding new team members to the system
- Reviewing architecture decisions with the team

## The C4 Model Approach

The C4 model provides a hierarchical way to visualize software architecture at different abstraction levels:

| Level | Diagram Type | Purpose | Target Audience |
|-------|-------------|---------|-----------------|
| **L1** | System Context | Shows the system and its external dependencies | Business stakeholders, PMs, non-technical |
| **L2** | Container | Shows main application boundaries and interactions | Technical leads, architects, developers |
| **L3** | Component | Shows internal structure of containers | Backend developers, team members |
| **L4** | Code | Shows implementation details (optional) | Developers working on specific modules |

### Key Principles

1. **Audience-First**: Choose the right abstraction level for your audience
2. **Visual-First**: Use diagrams over text whenever possible
3. **Progressive Disclosure**: Start high-level, then zoom in as needed
4. **Consistency**: Use consistent symbols, colors, and terminology
5. **Focus on Flows**: Highlight data flow and control flow clearly

## Recommended Slide Structure

For the detailed section-by-section slide structure, **please read `references/structure-template.md`**.

## Diagram Types and Best Practices

### System Context Diagram (C4 L1)

**Purpose**: Show the "big picture" - your system in its environment

**Elements to Include**:
- Your system (as a central box)
- External users/actors (person icons)
- External systems you depend on
- External systems that depend on you

**Tips**:
- Don't show internal components
- Label relationships with brief descriptions
- Use different shapes/colors for users vs systems

### Container Diagram (C4 L2)

**Purpose**: Show the high-level technology stack and how pieces fit together

**Elements to Include**:
- Web applications (single-page apps, mobile apps)
- APIs/microservices
- Databases
- Message queues/event streams
- File storage
- External services

**Key Information**:
- Technology choice for each container (e.g., "React", "Node.js API", "PostgreSQL")
- Communication protocols (REST, gRPC, WebSocket, etc.)
- Data flow directions

### Component Diagram (C4 L3)

**Purpose**: Show internal structure of a single container

**Use When**:
- Explaining complex internal logic
- Documenting responsibility segregation
- Onboarding developers to a specific service

**Elements to Include**:
- Components/modules within a container
- Interfaces between components
- External dependencies of the container

### Sequence Diagram

**Purpose**: Show time-ordered interactions for specific scenarios

**Best For**:
- API request/response flows
- Authentication sequences
- Multi-step business processes
- Error handling scenarios

**Tips**:
- Focus on one scenario per diagram
- Number the steps for easy reference
- Use loops/alt blocks for conditional logic

### Data Flow Diagram (DFD)

**Purpose**: Show how data moves through the system

**Notation**:
- Circles: Processes that transform data
- Arrows: Data movement (label with data name)
- Open rectangles: Data stores
- Closed rectangles: External entities

## Visual Design Guidelines

### Diagram Notation Standards

**Shapes**:
- **Rectangles**: Systems, containers, components
- **Person icons**: Users/actors
- **Cylinders**: Databases
- **Clouds**: External/cloud services
- **Arrows**: Relationships/flows (label clearly)

**Colors**:
- Use consistent color coding:
  - Your system: Primary brand color
  - External systems: Neutral/gray
  - Databases: Green or blue
  - Users: Orange or yellow
  - APIs: Distinct accent color

**Lines and Arrows**:
- **Solid lines**: Synchronous communication
- **Dashed lines**: Asynchronous/messaging
- **Bidirectional arrows**: Two-way communication
- **Number arrows** when sequence matters

## Content Best Practices

### Writing Guidelines

1. **Start with the Big Picture**: Always begin with context before diving into details
2. **Label Everything**: Every box, arrow, and shape should be clearly labeled
3. **Explain the "Why"**: Don't just show what - explain why this architecture was chosen
4. **Be Consistent**: Use the same names in diagrams as in code/documentation
5. **Avoid Acronyms**: Spell out terms at least once

### Key Information to Include

**For Each Diagram**:
- **Title**: What the diagram shows
- **Legend**: What symbols/colors mean
- **Scope**: What's included and excluded
- **Version**: When it was last updated

**Architecture Decision Explanations**:
| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| Microservices | Independent scaling | Operational complexity |
| PostgreSQL | ACID compliance | Horizontal scaling limits |
| REST API | Wide client support | Less efficient than gRPC |

### Common Mistakes to Avoid

1. **Overloading Diagrams**: One diagram = one concern. Split if too complex.
2. **Mixed Abstractions**: Don't mix context-level and component-level in one diagram
3. **Missing Labels**: Unlabeled arrows are ambiguous
4. **Technology Confusion**: Distinguish between "what" (function) and "how" (technology)
5. **Orphan Components**: Every component should connect to something

## Audience-Specific Guidance

### For Business Stakeholders
- Focus on System Context (C4 L1)
- Emphasize business capabilities and user value
- Minimize technical jargon
- Show integration points with external business systems

### For Technical Leads/Architects
- Include Container (C4 L2) and Component (C4 L3) diagrams
- Discuss technology choices and trade-offs
- Cover scalability, security, and operational aspects
- Include sequence diagrams for critical flows

### For New Team Members
- Start with System Context, then progressively reveal details
- Include data flow explanations
- Document naming conventions and patterns
- Show "where to find things" in the codebase

### For External Integrators
- Focus on API specifications and integration patterns
- Include authentication/authorization details
- Provide sequence diagrams for common integration scenarios
- Document rate limits and constraints

## Pre-Presentation Checklist

- [ ] Diagrams are readable at presentation resolution
- [ ] All elements are labeled clearly
- [ ] Legend is included for symbols/colors
- [ ] Technology choices are explained
- [ ] Key data flows are highlighted
- [ ] Scope of each diagram is clear
- [ ] Consistent terminology throughout
- [ ] Backup detail slides prepared for Q&A


## Workflow Handoff

Once the content structure and text are finalized based on these guidelines, **DO NOT generate the final Marp Markdown directly from this skill**.
Instead, hand off the implementation to the `marp-slide-creator` skill to ensure proper Marp syntax, layout, and overflow prevention.

> **Diagram Warning for Implementation Phase:** When suggesting diagrams (like Sequence or Flowcharts), remind the user that inline Mermaid (` ```mermaid `) fails in Marp PDF exports. Diagrams must be placed as placeholder images (`![Diagram](./assets/diagram.svg)`) and generated offline using Mermaid CLI during the implementation phase.

