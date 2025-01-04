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

### 4. Submit Drip Semester, Drop and Fail Courses
Submits courses to be dropped or marked as failed and returns updated study plan. In case that user requires dropping a semester, the frontend will send the request in "Drop".

**Endpoint:** `/submit_drop_fail_course`
- Method: POST
- Request Body:
```json
{
    "StdID": "integer",
    "Drop": [
        {
            "CID": "string",
            "Year": "integer",
            "Sem": "string"
        }
    ],
    "Fail": [
        {
            "CID": "string",
            "Year": "integer",
            "Sem": "string"
        }
    ]
}
```

**Response:**
```json
[
    {
        "CID": "string",
        "YEAR": "integer",
        "REGISTERSEM": "string",
        "GRADE": "string"
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
- `GRADE`: Achieved grade (can be letter grade or "Undefined")
- `CNAME`: Course name

### Course Fields
- `ID`: Course identifier
- `Name`: Course name
- `AllowedYear`: Eligible academic year
- `OpenSemester`: Semester when course is offered

### Drop/Fail Course Fields
- `CID`: Course ID to be dropped or marked as failed
- `Year`: Academic year of the course
- `Sem`: Semester of the course