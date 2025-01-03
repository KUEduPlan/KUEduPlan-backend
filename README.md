# API Backend Documentation

## Overview
This document outlines the endpoints and data structures for the student management system API.

## Endpoints

### 1. Student Data
Retrieves detailed information about a specific student.

**Endpoint:** `/student_data/{StdId}`
- Method: GET
- Parameters: 
  - `StdId` (integer): Student identification number

**Response:**
```json
{
    "NAME": "string",
    "YEAR": "integer",
    "PROGRAM": "string",
    "MID": "string",
    "DID": "string",
    "SEM": "string",
    "STATUS": "string"
}
```

### 2. Initial Study Plan
Retrieves the study plan for a specific student.

**Endpoint:** `/study_plan/{StdId}`
- Method: GET
- Parameters:
  - `StdId` (integer): Student identification number

**Response:**
```json
[
    {
        "CID": "string",
        "YEAR": "integer",
        "REGISTERSEM": "string",
        "GRADE": "string",
        "CNAME": "string"
    }
]
```

### 3. Pre-requisite Courses
Retrieves information about course prerequisites.

**Endpoint:** `/pre_course`
- Method: GET
- Parameters: None

**Response:**
```json
[
    {
        "PrerequisiteCourse": {
            "ID": "string",
            "Name": "string",
            "AllowedYear": "integer",
            "OpenSemester": "string"
        },
        "CurrentCourse": {
            "ID": "string",
            "Name": "string",
            "AllowedYear": "integer",
            "OpenSemester": "string"
        }
    }
]
```

## Data Types

### Student Data Fields
- `NAME`: Student's full name
- `YEAR`: Current academic year
- `PROGRAM`: Enrolled program name
- `MID`: Major ID
- `DID`: Department ID
- `SEM`: Current semester
- `STATUS`: Student's academic status

### Study Plan Fields
- `CID`: Course ID
- `YEAR`: Academic year
- `REGISTERSEM`: Registration semester
- `GRADE`: Achieved grade
- `CNAME`: Course name

### Course Fields
- `ID`: Course identifier
- `Name`: Course name
- `AllowedYear`: Eligible academic year
- `OpenSemester`: Semester when course is offered