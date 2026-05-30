# User Manual

## Introduction

CivicAssist AI helps citizens report civic issues quickly and efficiently.

---

## Accessing the Application

Launch the application using:

```bash
streamlit run frontend/app.py
```

The application opens in your browser.

---

## Submitting a Complaint

### Step 1

Open the Complaint Submission page.

### Step 2

Enter your complaint.

Example:

```text
The streetlight near Kukatpally Metro Station has not been working for 7 days.
```

### Step 3

Provide location information.

### Step 4

Click Submit.

---

## AI Processing

The system automatically:

* Detects complaint category
* Identifies responsible department
* Determines priority
* Generates complaint letter

---

## Download Complaint Letter

Click:

```text
Download PDF
```

to save the generated complaint.

---

## Email Submission

Click:

```text
Send Complaint
```

to email the complaint to the relevant department.

---

## Complaint Tracking

Navigate to:

```text
Complaint History
```

View:

* Complaint ID
* Status
* Department
* Submission Date

---

## Dashboard

Dashboard displays:

* Total complaints
* Department-wise complaints
* High-priority complaints
* Complaint trends

---

## Supported Complaint Types

* Streetlight Issues
* Potholes
* Garbage Overflow
* Water Leakage
* Drainage Problems

---

## Troubleshooting

### Backend Not Running

Verify:

```bash
uvicorn backend.main:app --reload
```

is active.

### Ollama Not Responding

Verify:

```bash
ollama run llama3
```

is running.

### Email Sending Failure

Verify:

* SMTP configuration
* Gmail App Password
* Internet connection

---

## Contact

For support, contact the project maintainers.
