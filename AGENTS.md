# AGENTS.md

## Project Overview

CivicAssist AI is an AI-powered civic grievance management platform that automates complaint classification, routing, generation, and tracking.

This document defines the logical agents used within the system.

---

# Agent 1: Complaint Classification Agent

## Responsibility

Analyze citizen complaints and identify issue categories.

## Inputs

* Complaint text

## Outputs

* Streetlight
* Pothole
* Garbage
* Water Leakage
* Drainage Issue

## Technologies

* Ollama
* Llama 3

---

# Agent 2: Department Routing Agent

## Responsibility

Determine the responsible department for each complaint.

## Inputs

* Complaint category

## Outputs

* Department Name
* Contact Information
* Priority Level

## Data Source

departments.json

---

# Agent 3: Complaint Generation Agent

## Responsibility

Generate formal complaint letters.

## Inputs

* Complaint category
* Complaint description
* Location

## Outputs

* Formal complaint document

## Technologies

* Llama 3

---

# Agent 4: PDF Generation Agent

## Responsibility

Convert generated complaint letters into PDF documents.

## Technologies

* ReportLab

---

# Agent 5: Email Dispatch Agent

## Responsibility

Send complaint letters to designated departments.

## Inputs

* Department Email
* Complaint PDF

## Technologies

* SMTP
* Gmail App Password

---

# Agent 6: Tracking Agent

## Responsibility

Maintain complaint records and statuses.

## Database

SQLite

## Statuses

* Submitted
* Assigned
* In Progress
* Resolved

---

# Agent Communication Flow

Citizen Complaint

↓

Classification Agent

↓

Routing Agent

↓

Complaint Generation Agent

↓

PDF Generation Agent

↓

Email Dispatch Agent

↓

Tracking Agent

---

# Future AI Agents

* Sentiment Analysis Agent
* Complaint Prioritization Agent
* Resolution Recommendation Agent
* Civic Analytics Agent
