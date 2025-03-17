from sre_compile import dis
from rule.assert_rule import *


def study_plan(stdID):
    # Retrieve data with fallback to empty lists if None is returned
    # course = required_course()
    # print("Course:", course)
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
    print(current_year, current_sem)

    remove_courses = set()


    for course in future:
        query_grade = list(prolog.query(f"recivedGrade('{stdID}', '{course['CID']}', CName, GRADE, YEAR, SEM)"))
        for i in range(len(query_grade)):
            query_grade[i]['CID'] = course['CID']
        # Check if the course is already passed
        for grade_entry in query_grade:
            if grade_entry['GRADE'] not in ["Undefined", "F"]:  # Passed courses
                remove_courses.add(grade_entry['CID'])

    # Filter out passed courses
    future = [course for course in future if course['CID'] not in remove_courses]

    # TODO: Added test
    for course in future:
        course_year = course['YEAR']
        course_sem = course['REGISTERSEM']

        if course_year < current_year and course_sem == 2:
            # If previous year's sem 2, register in current semester
            course['YEAR'], course['REGISTERSEM'] = current_year, current_sem
        elif course_year < course['REGISTERSEM'] and course_sem == 1:
            # If previous year's sem 1, register in next year's sem 1
            course['YEAR'], course['REGISTERSEM'] = current_year + 1, 1
        else:
            # Otherwise, keep the original registration year and semester
            course['YEAR'], course['REGISTERSEM'] = course_year, course_sem

        print(f"Course {course['CID']} should be registered in Year {course['YEAR']}, Semester {course['REGISTERSEM']}")


    grades = recieved_grade(stdID)

    for course_passed in passed:
        for course_grade in grades:
            if course_passed['CID'] == course_grade['CID']:
                course_passed['GRADE'] = course_grade['GRADE']
    
    for course_future in future:
        course_future['GRADE'] = 'Undefinded'

    grades_f = list(prolog.query(f"recivedGrade('{stdID}', CID, CName, 'F', YEAR, SEM)"))
    grades_w = list(prolog.query(f"recivedGrade('{stdID}', CID, CName, 'W', YEAR, SEM)"))
    for i in range(len(grades_f)):
        grades_f[i]['GRADE'] = 'F'
    for i in range(len(grades_w)):
        grades_w[i]['GRADE'] = 'W'
    results =  passed + grades_f + grades_w + future

    courses = required_course()

    for course in courses:
        for result in results:
            if result['CID'] == course['CID']:
                result['CNAME'] = course['CNAME']
    return results


# Normal case
# distribution_data = [{'CID' : '01417167', 'CNAME': 'คณิตศาสตร์วิศวกรรม I', 'STD_GOT_F': [{'STD_ID': '6410546131', 'STD_REGISTER_YEAR': 2563}], 'STD_PASSED': [{'STD_ID': '6410546133', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '789789', 'STD_REGISTER_YEAR': 2564}]},
#                      {'CID' : '01417168', 'CNAME': 'คณิตศาสตร์วิศวกรรม II', 'STD_GOT_F': [{'STD_ID': '6410546131', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '6410546133', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '789789', 'STD_REGISTER_YEAR': 2564}], 'STD_PASSED': [{}]},
#                      {'CID' : 'f1', 'CNAME': 'f1', 'STD_GOT_F': [{}], 'STD_PASSED': [{}]},
#                      {'CID' : 'f2', 'CNAME': 'f2', 'STD_GOT_F': [{'STD_ID': '6410', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '0876', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '789789', 'STD_REGISTER_YEAR': 2564}], 'STD_PASSED': [{'STD_ID': '34234', 'STD_REGISTER_YEAR': 2563}]}
#                      ]

# No passed pre
distribution_data = [{'CID' : '01417167', 'CNAME': 'คณิตศาสตร์วิศวกรรม I', 'STD_GOT_F': [{'STD_ID': '6410546131', 'STD_REGISTER_YEAR': 2563}], 'STD_PASSED': [{'STD_ID': '6410546133', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '64105461443', 'STD_REGISTER_YEAR': 2563}]},
                     {'CID' : '01417168', 'CNAME': 'คณิตศาสตร์วิศวกรรม II', 'STD_GOT_F': [{'STD_ID': '6410546131', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '6410546133', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '789789', 'STD_REGISTER_YEAR': 2564}], 'STD_PASSED': [{}]},
                     {'CID' : 'f1', 'CNAME': 'f1', 'STD_GOT_F': [{}], 'STD_PASSED': [{}]},
                     {'CID' : 'f2', 'CNAME': 'f2', 'STD_GOT_F': [{'STD_ID': '6410', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '0876', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '789789', 'STD_REGISTER_YEAR': 2564}], 'STD_PASSED': [{'STD_ID': '34234', 'STD_REGISTER_YEAR': 2563}]}
                     ]
def assert_data(student_code):
    assert_student_data(student_code)
    assert_required_course(student_code)
    assert_student_register(student_code)
    assert_student_grade_recived(student_code)
    assert_preco_course(student_code)
    assert_student_recived_grade_current_sem(student_code)

def open_plan_assert_data(student_code):
    assert_student_data(student_code)
    # assert_required_course(student_code)
    assert_student_register(student_code)
    assert_student_grade_recived(student_code)
    assert_preco_course(student_code)
    assert_student_recived_grade_current_sem(student_code)


def distribution(cid, pre_course_ids):
    # Iterate through distribution_data and count students who got 'F' for courses not in pre_course
    results = {}
    for course in distribution_data:
        if course['CID'] == cid:
            if course['CID'] not in pre_course_ids:
                for student in course.get('STD_GOT_F', []):
                    if len(student) != 0:
                        year = student['STD_REGISTER_YEAR']

                        if year in results.keys():
                            data = {
                                'CID': course['CID'],
                                'Ineligible': results[year]['Ineligible'] + 1
                            }
                        else:
                            data = {
                                'CID': course['CID'],
                                'Ineligible': 1
                            }
                        results[year] = data         
    if len(results) != 0:
        return results
    else:
        return "Subject had no data"    

def pre_sub_distribution(cid, pre_course_ids, pre_course):
    # Iterate through distribution_data and count students who got 'F' for courses not in pre_course
    results = {}
    for course in distribution_data:
            if course['CID'] == cid:
                if course['CID'] in pre_course_ids:
                    for i in range(len(pre_course)):
                        if course['CID'] == pre_course[i]['CID']:
                            print(pre_course[i]['PREID'])
                            for precourse in distribution_data:
                                if precourse['CID'] == pre_course[i]['PREID']:
                                    passed = passed_pre_std_f(precourse, course)
                                    passed_pre = passed_pre_std(precourse, precourse)
                                    print(passed_pre_std(precourse, precourse))
                                    for student in course.get('STD_GOT_F', []):
                                        if len(student) != 0:
                                            year = student['STD_REGISTER_YEAR']
                                            if year in results.keys():
                                                if year in passed.keys():
                                                    data = {
                                                        'CID': course['CID'],
                                                        'Ineligible': results[year]['Ineligible'] + 1,
                                                        'GOT_F_Passed_Pre': passed[year]['passed_pre']
                                                    }
                                                # if year in passed_pre.keys():
                                                #     pass
                                                else:
                                                    data = {
                                                        'CID': course['CID'],
                                                        'Ineligible': results[year]['Ineligible'] + 1,
                                                        'GOT_F_Passed_Pre': 0
                                    
                                                    }
                                            else:
                                                if year in passed.keys():
                                                    data = {
                                                        'CID': course['CID'],
                                                        'Ineligible': 1,
                                                        'GOT_F_Passed_Pre': passed[year]['passed_pre']
                                                    }
                                                else:
                                                    data = {
                                                        'CID': course['CID'],
                                                        'Ineligible': 1,
                                                        'GOT_F_Passed_Pre': 0
                                    
                                                    }
                                            results[year] = data
    if len(results) != 0:
        return results
    else:
        return "Subject had no data"  


def passed_pre_std_f(pre, cour):
    results = {}
    # Extract passed students from pre
    passed_students = {std['STD_ID']: std['STD_REGISTER_YEAR'] for std in pre['STD_PASSED']}

    # Check students in course STD_GOT_F who also passed pre
    for student in cour['STD_GOT_F']:
        std_id = student['STD_ID']
        if std_id in passed_students:
            year = passed_students[std_id]
            if year in results.keys():
                data = {
                            'passed_pre': results[year]['passed_pre'] + 1
                                                    
                        }
            else:
                data = {
                    'passed_pre': 1
                }
            results[year] = data
    return results

def passed_pre_std(pre, cour):
    results = {}
    # Extract passed students from pre
    passed_students = {std['STD_ID']: std['STD_REGISTER_YEAR'] for std in pre['STD_PASSED']}
    # return passed_students

    # Check students in course STD_GOT_F who also passed pre
    regis_std = []
    for student in cour['STD_GOT_F']:
        std_id = student['STD_ID']
        regis_std.append(std_id)
    for student in cour['STD_PASSED']:
        std_id = student['STD_ID']
        regis_std.append(std_id)
    for std in passed_students:
        year = passed_students[std_id]
        for regis_std_id in regis_std:
            if std not in regis_std_id:
                if year in results.keys():
                    data = {
                        'Eligible': results[year]['Eligible'] + 1
                    }
                else:
                    data = {
                        'Eligible': 1
                    }
                results[year] = data
    return results

def distribution_course():
    results = []
    for course in distribution_data:
        results.append({'CID': course['CID'], 'CNAME': course['CNAME']})
    return results