from pydantic import BaseModel
from typing import List, Optional

class StudentStatusRequest(BaseModel):
    student_code: str

class StudentStatusResponse(BaseModel):
    student_code: str
    first_name_th: str
    last_name_th: str
    campus_code: str
    faculty_code: str
    dept_code: str
    major_code: str
    campus_name_th: str
    faculty_name_th: str
    dept_name_th: str
    major_name_th: str
    entrance_year: int
    entrance_semester: int
    cur_id: int
    plan_id: int
    status_code: str
    status_code_desc: str
    status_id: str
    status_id_desc: str

class EnrollmentRequest(BaseModel):
    student_code: str

class EnrollmentResponse(BaseModel):
    academic_year: int
    semester: int
    subject_code: str
    subject_name: str
    enroll_status: str

class GradesRequest(BaseModel):
    student_code: str

class GradesResponse(BaseModel):
    academic_year: int
    semester: int
    subject_code: str
    subject_name: str
    grade: str

class EnrollmentSemesterRequest(BaseModel):
    student_code: str
    academic_year: int
    semester: int

class EnrollmentSemesterResponse(BaseModel):
    subject_code: str
    subject_name: str
    enroll_status: str
    instrs: Optional[List[dict]]
    schedules: Optional[List[str]]


# Models
class ProgramListRequest(BaseModel):
    campus_id: int
    faculty_id: int
    edulevel: str  # Values: bachelor, master, doctor

class ProgramListResponse(BaseModel):
    program_id: int
    program_name: str

class CurriculumListRequest(BaseModel):
    program_id: int

class CurriculumListResponse(BaseModel):
    cur_id: int
    cur_year: int

class PlanListRequest(BaseModel):
    cur_id: int

class PlanListResponse(BaseModel):
    plan_id: int
    plan_name: str

class StructureRequest(BaseModel):
    plan_id: int

class StructureResponse(BaseModel):
    group_no: str
    group_name: str
    group_min_credits: int
    group_max_credits: int

class PlanSubjectsRequest(BaseModel):
    plan_id: int

class PlanSubjectsResponse(BaseModel):
    class_year: int
    semester: int
    group_no: str
    group_name: str
    subject_code: str
    subject_name: str

class PrecoSubjectsRequest(BaseModel):
    plan_id: int

class PrecoSubjectsResponse(BaseModel):
    subject_code: str
    subject_name: str
    preco_code: str
    preco_name: str
    preco_type: str

class CourseDetail(BaseModel):
    CID: str
    Year: int
    Sem: str
    Type: str

# Define the request body model
class DropFailCourseRequest(BaseModel):
    StdID: int
    Courses: List[CourseDetail]

class Login(BaseModel):
    Username: str
    Password: str

class Tokens(BaseModel):
    StdID: int
    Tokens: str