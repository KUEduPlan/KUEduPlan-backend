from rule.assert_rule import *
from database.student_database import insert_open_plan_data

def assert_required_course_open_plan(plan_id):
    db = connect_mongo("Curriculumn")
    collection = db["PlanSubject"]
    course_data = collection.find_one({"plan_id": plan_id})
    plan_subject = course_data['plan_subject']
    for i in range(len(plan_subject)):
        plan_subject[i]['subject_code'] = plan_subject[i]['subject_code'].split('-')[0]
    key_mapping = {
    "CID": "subject_code",
    "CNAME": "subject_name",
    "GID": "group_no",
    "GNAME": "group_name",
    "ALLOWYEAR": "class_year",
    "OPENSEM": "semester"
    }
    plan_subject = [
    {new_key: item[old_key] for new_key, old_key in key_mapping.items()}
    for item in plan_subject
    ]
    
    insert_open_plan_data(plan_id, plan_subject)
    for i in range(len(plan_subject)):
        prolog.assertz(
            f"course('{plan_subject[i]['CID']}', '{plan_subject[i]['CNAME']}', '{plan_subject[i]['GID']}', '{plan_subject[i]['GNAME']}', {plan_subject[i]['ALLOWYEAR']}, {plan_subject[i]['OPENSEM']})"
        )

def assert_open_plan(plan_id):
    db = connect_mongo("Plan")
    collection = db["OpenPlan"]
    course_data = collection.find_one({"Plan_ID": plan_id})
    plan_subject = course_data['Open_Plan']
    for i in range(len(plan_subject)):
        prolog.assertz(
            f"course('{plan_subject[i]['CID']}', '{plan_subject[i]['CNAME']}', '{plan_subject[i]['GID']}', '{plan_subject[i]['GNAME']}', {plan_subject[i]['ALLOWYEAR']}, {plan_subject[i]['OPENSEM']})"
        )

def open_plan(plan_id):
    db = connect_mongo("Plan")
    collection = db["OpenPlan"]
    course_data = collection.find_one({"Plan_ID": plan_id})
    if course_data:
        assert_open_plan(plan_id)
        print('1')
    else: 
        assert_required_course_open_plan(plan_id)
        print('2')

def open_study_plan(stdID, courses):
    # Retrieve data with fallback to empty lists if None is returned
    # course = required_course()
    passed = passed_courses(stdID)
    future_data = future_course(stdID) + future_fail_course(stdID)
    df = pd.DataFrame(future_data)
    df['YEAR'] = df['YEAR'] % 100
    df_unique = df.drop_duplicates()
    future = df_unique.to_dict(orient='records')


    # Find max YEAR
    max_year = max(course['YEAR'] for course in passed)

    # Filter courses with max YEAR
    filtered_by_year = [course for course in passed if course['YEAR'] == max_year]

    # Find max SEM from the filtered courses
    max_sem = max(course['SEM'] for course in filtered_by_year)

    # Filter courses with max SEM
    max_y_s_p = [course for course in filtered_by_year if course['SEM'] == max_sem]

    if max_y_s_p[0]['SEM'] == 2:
        max_y_s_p[0]['SEM'] = 1
        max_y_s_p[0]['YEAR'] = max_y_s_p[0]['YEAR'] + 1
    if max_y_s_p[0]['SEM'] == 1:
        max_y_s_p[0]['SEM'] = 2
    current_year = max_y_s_p[0]['YEAR']
    current_sem = max_y_s_p[0]['SEM']

    remove_courses = set()
    for course in future:
        query_grade = list(prolog.query(f"recivedGrade('{stdID}', '{course['CID']}', CNAME, GRADE, YEAR, SEM)"))
        for i in range(len(query_grade)):
            query_grade[i]['CID'] = course['CID']
        # Check if the course is already passed
        for grade_entry in query_grade:
            if grade_entry['GRADE'] not in ["Undefined", "F"]:  # Passed courses
                remove_courses.add(grade_entry['CID'])

    # Filter out passed courses
    future = [course for course in future if course['CID'] not in remove_courses]
    # print(future)
    # TODO: Added test
    for course in future:
        course_year = course['YEAR']
        course_sem = course['SEM']

        if course_year < current_year and course_sem == 2:
            # If previous year's sem 2, register in current semester
            course['YEAR'], course['SEM'] = current_year, current_sem
        elif course_year < course['SEM'] and course_sem == 1:
            # If previous year's sem 1, register in next year's sem 1
            course['YEAR'], course['SEM'] = current_year + 1, 1
        else:
            # Otherwise, keep the original registration year and semester
            course['YEAR'], course['SEM'] = course_year, course_sem

        print(f"Course {course['CID']} should be registered in Year {course['YEAR']}, Semester {course['SEM']}")


    grades = recieved_grade(stdID)
    
    studen_data = list(prolog.query(f"student('{stdID}', StdFirstName, StdLastName, CID, FID, DID, MID, CurID, PlanID, StdRegisterYear, Status, StdSem)"))
    student_current_year = (time.localtime().tm_year + 543 - 1) % 100
    student_current_sem = studen_data[0]['StdSem']
    # print(student_current_year, student_current_sem)
    
    future = [course for course in future if not (course['YEAR'] < student_current_year or course['SEM'] < student_current_sem)]
    # print(future)
    for course_passed in passed:
        for course_grade in grades:
            if course_passed['CID'] == course_grade['CID']:
                course_passed['GRADE'] = course_grade['GRADE']
    
    for course_future in future:
        course_future['GRADE'] = 'Undefined'

    grades_f = list(prolog.query(f"recivedGrade('{stdID}', CID, CNAME, 'F', YEAR, SEM)"))
    grades_w = list(prolog.query(f"recivedGrade('{stdID}', CID, CNAME, 'W', YEAR, SEM)"))
    for i in range(len(grades_f)):
        grades_f[i]['GRADE'] = 'F'
    for i in range(len(grades_w)):
        grades_w[i]['GRADE'] = 'W'
    results =  passed + grades_f + grades_w + future
    for course in courses:
        for result in results:
            if result['CID'] == course['CID']:
                result['CNAME'] = course['CNAME']
                result['GID'] = course['GID']
    return results