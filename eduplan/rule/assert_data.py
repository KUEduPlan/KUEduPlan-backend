from eduplan.database.connect_database import connect_mongo
from pyswip import Prolog
import pandas as pd
import time

prolog = Prolog()

def assert_student_data(student_code):
    db = connect_mongo("Student")
    collection = db["StudentStatus"]
    student_data = collection.find_one({"student_code": student_code})
    prolog.assertz(f"student('{student_code}', '{student_data['first_name_th']}', '{student_data['last_name_th']}', '{student_data['campus_code']}', '{student_data['faculty_code']}', '{student_data['dept_code']}', '{student_data['major_code']}', {student_data['cur_id']}, {student_data['plan_id']}, {student_data['entrance_year'] - 1 }, {student_data['status_id']}, 2)")


def assert_student_register(student_code):
    db = connect_mongo("Student")
    collection = db["StudentEnrollment"]
    student_enrollment = collection.find_one({"student_code": student_code})['enrollment']
    df = pd.DataFrame(student_enrollment)
    filtered_df = df[df['enroll_status'].isin(['A', 'W'])]

    enrollment_data = filtered_df.to_dict(orient='records')
    for i in range(len(enrollment_data)):
        prolog.assertz(
            f"register('{student_code}', '{enrollment_data[i]['subject_code']}', '{enrollment_data[i]['subject_name']}', {enrollment_data[i]['academic_year']}, {enrollment_data[i]['semester']})"
        )

def assert_student_grade_recived(student_code):
    db = connect_mongo("Student")
    collection = db["StudentGrades"]
    student_grades = collection.find_one({"student_code": student_code})['grades']
    # 'academic_year': 0, 'semester': 0 Transfer Course
    for i in range(len(student_grades)):
        prolog.assertz(
            f"recivedGrade('{student_code}', '{student_grades[i]['subject_code']}', '{student_grades[i]['subject_name']}', '{student_grades[i]['grade']}', {student_grades[i]['academic_year']}, {student_grades[i]['semester']})"
        )

def assert_required_course(student_code):
    results = list(prolog.query(f"student('{student_code}', StdFirstName, StdLastName, CID, FID, DID, MID, CurID, PlanID, StdRegisterYear, Status, StdSem)"))

    db = connect_mongo("Curriculumn")
    collection = db["PlanSubject"]
    course_data = collection.find_one({"plan_id": results[0]['PlanID']})
# course(CID, CNAME, GID, GName, ALLOWYEAR : int, OPENSEM) 
    plan_subject = course_data['plan_subject']
    for i in range(len(plan_subject)):
        plan_subject[i]['subject_code'] = plan_subject[i]['subject_code'].split('-')[0]
        prolog.assertz(
            f"course('{plan_subject[i]['subject_code']}', '{plan_subject[i]['subject_name']}', '{plan_subject[i]['group_no']}', '{plan_subject[i]['group_name']}', {plan_subject[i]['class_year']}, {plan_subject[i]['semester']})"
        )

def assert_preco_course(student_code):
    results = list(prolog.query(f"student('{student_code}', StdFirstName, StdLastName, CID, FID, DID, MID, CurID, PlanID, StdRegisterYear, Status, StdSem)"))
    db = connect_mongo("Curriculumn")
    collection = db["PreCoSubject"]
    course_data = collection.find_one({"plan_id": results[0]['PlanID']})
    preco_subject = course_data['preco_subject']

    df = pd.DataFrame(preco_subject)
    filtered_df_pre = df[df['preco_type'].isin(['pre'])]
    filtered_df_co = df[df['preco_type'].isin(['co'])]
    pre_course = filtered_df_pre.to_dict(orient='records')
    co_course = filtered_df_co.to_dict(orient='records')

    for i in range(len(pre_course)):
        pre_course[i]['preco_code'] = pre_course[i]['preco_code'].split('-')[0]
        pre_course[i]['subject_code'] = pre_course[i]['subject_code'].split('-')[0]
        prolog.assertz(
            f"directPrerequisiteOf('{pre_course[i]['preco_code']}', '{pre_course[i]['subject_code']}')"
        )

    for i in range(len(co_course)):
        co_course[i]['preco_code'] = co_course[i]['preco_code'].split('-')[0]
        co_course[i]['subject_code'] = co_course[i]['subject_code'].split('-')[0]
        prolog.assertz(
            f"corequisiteOf('{co_course[i]['preco_code']}', '{co_course[i]['subject_code']}')"
        )

def assert_student_recived_grade_current_sem(student_code):
    std_db = connect_mongo("Student")
    std_collection = std_db["StudentGrades"]
    student_grades = std_collection.find_one({"student_code": student_code})['grades']

    results = list(prolog.query(f"student('{student_code}', StdFirstName, StdLastName, CID, FID, DID, MID, CurID, PlanID, StdRegisterYear, Status, StdSem)"))
    db = connect_mongo("Curriculumn")
    collection = db["PlanSubject"]
    course_data = collection.find_one({"plan_id": results[0]['PlanID']})['plan_subject']
    for i in range(len(course_data)):
        course_data[i]['subject_code'] = course_data[i]['subject_code'].split('-')[0]
    # Create pandas DataFrames
    df_student = pd.DataFrame(student_grades)
    df_course = pd.DataFrame(course_data)

    # Find the subject_codes in student data that are not in course data
    subject_codes_in_student_not_in_course = df_course[~df_course['subject_code'].isin(df_student['subject_code'])]
    undefined_course_data = subject_codes_in_student_not_in_course.to_dict(orient='records')

    for i in range(len(undefined_course_data)):
        undefined_course_data[i]['class_year'] = (undefined_course_data[i]['class_year'] + results[0]['StdRegisterYear'] - 1) % 100
        undefined_course_data[i]['subject_code'] = undefined_course_data[i]['subject_code']
        prolog.assertz(
            f"recivedGrade('{student_code}', '{undefined_course_data[i]['subject_code']}', '{undefined_course_data[i]['subject_name']}', 'Undefined', {undefined_course_data[i]['class_year']}, {undefined_course_data[i]['semester']})"
        )

def assert_student_recived_grade_current_sem_open_plan(student_code):
    std_db = connect_mongo("Student")
    std_collection = std_db["StudentGrades"]
    student_grades = std_collection.find_one({"student_code": student_code})['grades']

    results = list(prolog.query(f"student('{student_code}', StdFirstName, StdLastName, CID, FID, DID, MID, CurID, PlanID, StdRegisterYear, Status, StdSem)"))
    db = connect_mongo("Plan")
    collection = db["OpenPlan"]
    course_data = collection.find_one({"Plan_ID": results[0]['PlanID']})['Open_Plan']

    # Create pandas DataFrames
    df_student = pd.DataFrame(student_grades)
    df_course = pd.DataFrame(course_data)

    # Find the subject_codes in student data that are not in course data
    # subject_codes_in_student_not_in_course = df_course[~df_course['CID'].isin(df_student['subject_code'])]
    subject_codes_in_student_not_in_course = df_course[
    ~df_course.set_index(['CID', 'OPENSEM']).index.isin(df_student.set_index(['subject_code', 'semester']).index)
    ]

    # Sample DataFrames (Assuming they are already defined)
    subject_codes_in_student_not_in_course = subject_codes_in_student_not_in_course.copy()
    df_student = df_student.copy()

    # Filter df_student to only include rows where grade is not 'F'
    valid_subjects = df_student[df_student["grade"] != "F"]["subject_code"].unique()

    # Filter out rows from subject_codes_in_student_not_in_course where CID is in valid_subjects
    subject_codes_in_student_not_in_course = subject_codes_in_student_not_in_course[
        ~subject_codes_in_student_not_in_course["CID"].isin(valid_subjects)
    ]

    # Display the updated DataFrame
    undefined_course_data = subject_codes_in_student_not_in_course.to_dict(orient='records')

    # print(undefined_course_data)
    for i in range(len(undefined_course_data)):
        undefined_course_data[i]['ALLOWYEAR'] = (undefined_course_data[i]['ALLOWYEAR'] + results[0]['StdRegisterYear'] - 1) % 100
        undefined_course_data[i]['CID'] = undefined_course_data[i]['CID']
        prolog.assertz(
            f"recivedGrade('{student_code}', '{undefined_course_data[i]['CID']}', '{undefined_course_data[i]['CNAME']}', 'Undefined', {undefined_course_data[i]['ALLOWYEAR']}, {undefined_course_data[i]['OPENSEM']})"
        )
# Query for passed courses
def student_data(stdID):
    results = list(prolog.query(f"student('{stdID}', StdFirstName, StdLastName, CID, FID, DID, MID, CurID, PlanID, StdRegisterYear, Status, StdSem)"))
    return results

def register_data(stdID):
    results = list(prolog.query(f"register('{stdID}', CId, CName, RegisterYear, OpenSem)"))
    return results

def recieved_grade(stdID):
    results = list(prolog.query(f"recivedGrade('{stdID}', CID, CName, GRADE, YEAR, SEM)"))
    return results

def required_course():
    results = list(prolog.query("course(CID, CNAME, GID, GName, ALLOWYEAR, OPENSEM)"))
    return results

def pre_Course():
    results = list(prolog.query("directPrerequisiteOf(PreCID, CID)"))
    return results

def co_course():
    results = list(prolog.query("corequisiteOf(CoCID, CID)"))
    return results