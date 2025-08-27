# Generex Agent Features

## Agent Overview

This document provides detailed information about the four core business agents in the Generex Orchestration System: Appointment, Support, Estimate, and Advisor. Each agent is designed to handle specific business workflows and customer interactions.

## 📅 **Appointment Node**

**Purpose**: Manages appointment booking and scheduling

**Dependencies**: Calendar data, availability

**Key Functions**:
- Books appointments
- Manages scheduling conflicts
- Handles rescheduling requests

**Step-wise Functionality**:
1. Enforce appointment SOPs
2. Determine if appointment should be created
3. Create appointment if required
4. Use tools for appointment management
5. Handle scheduling conflicts and rescheduling requests
6. Output appointment confirmations and calendar updates

**Business Value**:
- **Scheduling Management**: Book appointments to drive revenue
- **Calendar Optimization**: Maximize business capacity utilization
- **Conflict Resolution**: Handle scheduling conflicts professionally
- **Confirmation Process**: Ensure appointment reliability and reduce no-shows

**Tools Used**: 
- Uses appointment management tools (specific tool names not detailed in the documentation)
- SOP enforcement using `sop_enforcer` template

**Output**: Appointment confirmations and calendar updates

## 🛠️ **Support Node**

**Purpose**: Handles customer support requests with SOP enforcement

**Dependencies**: Support tickets, service history, SOP checklists

**Specific Work**:
- **Enforces support SOPs** using `sop_enforcer` template and `sop_checklists/support`
- **Manages dynamic SOPs** for complex support workflows
- **Creates support tickets** using `SupportTool`
- **Handles warranty claims** and service requests
- **Processes service warranty reports** with dynamic SOP enforcement
- **Uses tool integration** for support operations

**Key Capabilities**:
- SOP enforcement and validation
- Dynamic SOP management
- Ticket creation and management
- Warranty claim processing

**Step-wise Functionality**:
1. Enforce support SOPs using `sop_enforcer` template and `sop_checklists/support`
2. Manage dynamic SOPs for complex support workflows
3. Create support tickets using `SupportTool`
4. Handle warranty claims and service requests
5. Process service warranty reports with dynamic SOP enforcement
6. Use tool integration for support operations
7. Store report data and finalize service warranty reports
8. Output support responses, SOP steps, and ticket information

**Tools Used**:
- `SupportTool` for support ticket management
- `sop_enforcer` template for SOP enforcement
- `sop_checklists/support` for support workflow steps

**Business Value**:
- **Issue Resolution**: Solve customer problems to maintain satisfaction
- **Ticket Management**: Track and manage support requests efficiently
- **Warranty Processing**: Handle warranty claims for customer retention
- **Service Documentation**: Maintain records for business intelligence
- **Quality Assurance**: Ensure support meets business standards

**Output**: Support responses, SOP steps, and ticket information

## 💰 **Estimate Node**

**Purpose**: Handles price estimation and quotes with comprehensive workflow

**Dependencies**: Service catalog, pricing data, SOP checklists

**Specific Work**:
- **Manages service selection** and service details
- **Verifies property addresses** for accurate estimates
- **Processes image uploads** for visual assessment
- **Enforces estimation SOPs** using `sop_enforcer` and `sop_checklists/estimate`
- **Handles dynamic SOPs** for complex estimation scenarios
- **Uses `EstimationTool`** for price calculations and service management
- **Finalizes estimate reports** with comprehensive pricing

**Key Capabilities**:
- Service catalog management
- Address verification
- Image processing
- Dynamic SOP enforcement
- Price calculation

**Step-wise Functionality**:
1. Route to appropriate estimation workflow (verify address, get services, etc.)
2. Manage service selection and service details
3. Verify property addresses for accurate estimates
4. Process image uploads for visual assessment
5. Enforce estimation SOPs using `sop_enforcer` and `sop_checklists/estimate`
6. Handle dynamic SOPs for complex estimation scenarios
7. Use `EstimationTool` for price calculations and service management
8. Store report data and finalize estimate reports
9. Output estimates, pricing information, and service details

**Tools Used**:
- `EstimationTool` for price calculations and service management
- `sop_enforcer` template for SOP enforcement
- `sop_checklists/estimate` for estimation requirements and service details

**Business Value**:
- **Service Assessment**: Evaluate customer needs for accurate pricing
- **Address Verification**: Ensure service delivery feasibility
- **Visual Analysis**: Process images for accurate cost estimation
- **Price Calculation**: Generate competitive and profitable quotes
- **Service Documentation**: Create detailed estimates for business records

**Output**: Estimates, pricing information, and service details

## 🎯 **Advisor Node**

**Purpose**: Provides general information and advice

**Dependencies**: Knowledge base, company information

**Key Functions**:
- Answers general questions
- Provides recommendations
- Shares company information

**Step-wise Functionality**:
1. Retrieve relevant information using retriever
2. Process advisor logic for information provision
3. Present recommendations and company information
4. Answer general questions and provide advice
5. Output informational responses

**Tools Used**:
- `retriever` for data retrieval and service catalog access
- `advisor` template for information provision and recommendations

**Business Value**:
- **Information Provision**: Share knowledge to build customer trust
- **Recommendation Engine**: Suggest relevant services for upselling
- **Educational Support**: Help customers make informed decisions
- **Brand Building**: Position company as knowledgeable industry expert

**Output**: Informational responses

## Tools Summary

| Agent | Primary Tools | Templates |
|-------|---------------|-----------|
| **Appointment** | Appointment management tools | `sop_enforcer`, `appointment` |
| **Support** | `SupportTool` | `sop_enforcer`, `sop_checklists/support` |
| **Estimate** | `EstimationTool` | `sop_enforcer`, `sop_checklists/estimate`, `estimate` |
| **Advisor** | `retriever` | `advisor` |

## Workflow Integration

All four agents follow SOP (Standard Operating Procedure) enforcement patterns and integrate with the broader workflow through the Execution Report Analyzer, which processes their outputs and provides summaries to the Planner for conversation strategy.

### Data Flow
- **Input**: User requests routed through the Router Node
- **Processing**: Each agent handles its specific business logic
- **Output**: Results sent to Execution Report Analyzer
- **Integration**: Analyzer provides summaries to Planner for conversation strategy
- **Response**: Generator creates final user responses based on agent outputs
