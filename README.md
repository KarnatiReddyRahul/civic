# CivicAssist AI

## Overview

CivicAssist AI is an AI-powered Civic Grievance Management Platform designed to simplify how citizens report civic issues. Citizens often struggle to identify the correct government department, write formal complaints, and track issue resolution.

CivicAssist AI allows users to describe a civic problem in natural language and automatically:

* Classifies the issue
* Identifies the responsible department
* Generates a formal complaint letter
* Creates a downloadable PDF
* Sends complaints via email
* Tracks complaint status
* Provides analytics dashboards

---

## Problem Statement

Citizens frequently face challenges in reporting civic issues such as:

* Broken streetlights
* Potholes
* Garbage overflow
* Water leakage
* Drainage problems

Most existing systems require users to manually identify departments and prepare complaint documents.

---

## Solution

CivicAssist AI uses Artificial Intelligence to automate complaint processing and routing.

### Workflow

Citizen Complaint
→ AI Classification
→ Department Routing
→ Complaint Letter Generation
→ PDF Creation
→ Email Dispatch
→ Complaint Tracking

---

## Features

### Citizen Portal

* Submit complaints using natural language
* Voice-based complaint input
* Multilingual support
* Download complaint PDF
* Complaint tracking

### AI Engine

* Complaint classification
* Department identification
* Priority assessment
* Complaint letter generation

### Admin Dashboard

* Complaint statistics
* Department-wise analytics
* Complaint status tracking
* Resolution monitoring

---

## Tech Stack

### Frontend

* Streamlit

### Backend

* FastAPI

### Database

* SQLite

### AI

* Ollama
* Llama 3

### Additional Tools

* ReportLab
* Plotly
* SMTP Email Service

---

## Project Structure

```text
civicassist-ai/

├── app.py
├── pages/
│   ├── 1_Report_Issue.py
│   ├── 2_Complaint_History.py
│   ├── 3_Admin_Dashboard.py
│   └── 4_AI_Complaint_View.py
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── db_helper.py
│   ├── models.py
│   ├── routers/
│   └── services/
├── requirements.txt
├── README.md
├── CONTRIBUTING.md
├── USER_MANUAL.md
└── AGENTS.md
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd civicassist-ai
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Ollama

```bash
ollama pull llama3
```

### Run Backend

```bash
uvicorn backend.main:app --reload
```

### Run Frontend

```bash
streamlit run app.py
```

> Note: Start the backend first so the frontend pages that use the API can connect properly.

### Streamlit Cloud Deployment

This app can run on Streamlit Cloud without a separate FastAPI server by using the local backend helpers and SQLite database.

If you want to deploy only the frontend on Streamlit Cloud, no backend `uvicorn` process is required. The app will use local database calls by default.

If you prefer to use a separate backend service instead, set the following environment variables in Streamlit Cloud:

```bash
API_BASE=https://your-backend.example.com
AI_GENERATOR_BASE=https://your-model-host
```

If `API_BASE` is not set, the app uses the bundled backend logic directly.

---

## Future Enhancements

* Direct government API integration
* Mobile application
* GIS complaint heatmaps
* AI-powered resolution recommendations
* Department performance analytics

---

## Team

Developed during a CivicTech Hackathon.

## License

MIT License
