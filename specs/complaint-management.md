# Complaint Management Specification

This specification documents the Citizen Complaint Management flow, routing rules, database models, and states.

## Complaint States

Each citizen grievance follows a strict state transition model:
1. **Submitted**: Grievance received. Classification and routing agents trigger.
2. **Assigned**: Grievance assigned to the responsible municipal department.
3. **In Progress**: Remediation work started by department officials.
4. **Resolved**: Grievance solved, citizens notified.

## Department Routing Rules

Complaints are categorized into one of five categories, mapped to target municipal departments defined in `departments.json`:

| Category | Department | Priority |
|---|---|---|
| Streetlight | Electrical Department | Medium |
| Pothole | Road Operations Department | High |
| Garbage | Sanitation Department | Low |
| Water Leakage | Water Supply Department | Medium |
| Drainage Issue | Sewage & Water Department | High |

## Database Schema (SQLAlchemy Model)

- `id`: Integer (Primary Key)
- `complaint_id`: String(8) (Unique ID)
- `citizen_name`: String
- `email`: String
- `phone`: String
- `complaint_text`: String
- `issue_category`: String
- `department`: String
- `department_email`: String
- `priority`: String
- `location`: String
- `latitude`: Float
- `longitude`: Float
- `generated_letter`: String
- `status`: String (Default: "Submitted")
- `email_sent`: Boolean (Default: False)
- `pdf_path`: String
- `created_at`: DateTime (Default: UTC now)
- `updated_at`: DateTime (Default: UTC now)
