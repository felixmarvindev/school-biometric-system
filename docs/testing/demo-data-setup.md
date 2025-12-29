# Demo Data Setup

## Overview

This guide explains how to set up realistic demo data for testing and demonstrations.

## Demo Data Scripts

### SQL Scripts

Create SQL scripts to insert demo data:

```sql
-- Insert demo school
INSERT INTO schools (name, code, address, phone, email) VALUES
('Greenfield Academy', 'GFA-001', 'Nairobi, Kenya', '+254 712 345 678', 'admin@greenfield.ac.ke');

-- Insert demo admin user
INSERT INTO users (school_id, email, full_name, password_hash) VALUES
(1, 'admin@greenfield.ac.ke', 'John Doe', '$2b$12$...'); -- Use bcrypt hash

-- Insert demo classes
INSERT INTO classes (school_id, name, level) VALUES
(1, 'Grade 1', 1),
(1, 'Grade 2', 2),
(1, 'Form 1', 7),
(1, 'Form 2', 8);

-- Insert demo streams
INSERT INTO streams (class_id, name) VALUES
(1, 'A'),
(1, 'B'),
(3, 'A'),
(3, 'B');

-- Insert demo students
INSERT INTO students (school_id, admission_number, first_name, last_name, stream_id, parent_phone) VALUES
(1, '001', 'Jane', 'Smith', 1, '+254 712 111 111'),
(1, '002', 'John', 'Doe', 1, '+254 712 222 222'),
(1, '003', 'Mary', 'Johnson', 3, '+254 712 333 333');

-- Insert demo devices
INSERT INTO devices (school_id, name, ip_address, port, location) VALUES
(1, 'Main Gate Scanner', '192.168.1.100', 4370, 'Main Gate'),
(1, 'Library Scanner', '192.168.1.101', 4370, 'Library');
```

## Demo Data Files

### JSON Fixtures

Create JSON files for programmatic data insertion:

```json
{
  "schools": [
    {
      "name": "Greenfield Academy",
      "code": "GFA-001",
      "address": "Nairobi, Kenya",
      "phone": "+254 712 345 678",
      "email": "admin@greenfield.ac.ke"
    }
  ],
  "students": [
    {
      "admission_number": "001",
      "first_name": "Jane",
      "last_name": "Smith",
      "parent_phone": "+254 712 111 111"
    }
  ]
}
```

## Realistic Data

### Student Names
Use common Kenyan names:
- First Names: Jane, John, Mary, Peter, Sarah, David, Grace, James
- Last Names: Smith, Doe, Johnson, Ochieng, Wanjiru, Kipchoge

### Admission Numbers
- Format: 001, 002, 003... or GFA-001, GFA-002
- Ensure uniqueness

### Phone Numbers
- Format: +254 7XX XXX XXX
- Use realistic prefixes

### Dates
- Use recent dates for demo
- Dates of birth: 2008-2015 for primary, 2006-2009 for secondary

## Demo Scenarios

### Scenario 1: New School Setup
- 1 school
- 1 admin user
- 5-10 students
- 2-3 devices

### Scenario 2: Established School
- 1 school
- 1 admin user
- 50-100 students
- 5-10 devices
- Some enrollments
- Some attendance records

### Scenario 3: Multi-School
- 2-3 schools
- Multiple admin users
- Students per school
- Devices per school

## Setup Instructions

### 1. Clear Existing Data (Optional)
```sql
TRUNCATE TABLE attendance_records CASCADE;
TRUNCATE TABLE enrollments CASCADE;
TRUNCATE TABLE students CASCADE;
-- ... etc
```

### 2. Run Demo Data Script
```bash
psql -d school_biometric -f demo-data.sql
```

### 3. Verify Data
- Check database for inserted records
- Verify relationships are correct
- Test with application

## Demo Data Maintenance

### Keep Data Fresh
- Update dates regularly
- Refresh attendance records
- Add new students occasionally

### Reset for Demos
- Clear sensitive data
- Reset to clean state
- Run demo data script

---

**Use realistic data to make demos more convincing and tests more valuable!**

