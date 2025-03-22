from rule.assert_rule import *
from collections import Counter

# Normal case
# distribution_data = [{'CID' : '01417167', 'CNAME': 'คณิตศาสตร์วิศวกรรม I', 'STD_GOT_F': [{'STD_ID': '6410546131', 'STD_REGISTER_YEAR': 2563}], 'STD_PASSED': [{'STD_ID': '6410546133', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '789789', 'STD_REGISTER_YEAR': 2564}]},
#                      {'CID' : '01417168', 'CNAME': 'คณิตศาสตร์วิศวกรรม II', 'STD_GOT_F': [{'STD_ID': '6410546131', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '6410546133', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '789789', 'STD_REGISTER_YEAR': 2564}], 'STD_PASSED': [{}]},
#                      {'CID' : 'f1', 'CNAME': 'f1', 'STD_GOT_F': [{}], 'STD_PASSED': [{}]},
#                      {'CID' : 'f2', 'CNAME': 'f2', 'STD_GOT_F': [{'STD_ID': '6410', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '0876', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '789789', 'STD_REGISTER_YEAR': 2564}], 'STD_PASSED': [{'STD_ID': '34234', 'STD_REGISTER_YEAR': 2563}]}
#                      ]

# No passed pre
distribution_data = [{'CID' : '01417167', 'CNAME': 'คณิตศาสตร์วิศวกรรม I', 'STD_GOT_F': [{'STD_ID': '6410546131', 'STD_REGISTER_YEAR': 2563}], 'STD_PASSED': [{'STD_ID': '6410546133', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '64105461443', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '3', 'STD_REGISTER_YEAR': 2563}]},
                     {'CID' : '01417168', 'CNAME': 'คณิตศาสตร์วิศวกรรม II', 'STD_GOT_F': [{'STD_ID': '6410546131', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '6410546133', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '789789', 'STD_REGISTER_YEAR': 2564}], 'STD_PASSED': [{}]},
                     {'CID' : 'f1', 'CNAME': 'f1', 'STD_GOT_F': [{}], 'STD_PASSED': [{}]},
                     {'CID' : 'f2', 'CNAME': 'f2', 'STD_GOT_F': [{'STD_ID': '6410', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '0876', 'STD_REGISTER_YEAR': 2563}, {'STD_ID': '789789', 'STD_REGISTER_YEAR': 2564}], 'STD_PASSED': [{'STD_ID': '34234', 'STD_REGISTER_YEAR': 2563}]}
                     ]


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
                                'Ineligible': results[year]['Ineligible'] + 1,
                                'Eligible': 0
                            }
                        else:
                            data = {
                                'CID': course['CID'],
                                'Ineligible': 1,
                                'Eligible': 0
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
                            for precourse in distribution_data:
                                if precourse['CID'] == pre_course[i]['PREID']:
                                    passed = passed_pre_std_f(precourse, course)
                                    eligible = eligible_passed_pre_std(precourse, course)
                      
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
                                    for key in results.keys():
                                        if key in eligible:
                                            results[key]['Eligible'] = eligible[key]
                                        else:
                                            results[key]['Eligible'] = 0
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

def eligible_passed_pre_std(pre, cour):
    # Extract passed students from pre
    passed_students = {std['STD_ID']: std['STD_REGISTER_YEAR'] for std in pre['STD_PASSED']}
    # return passed_students
    # Check students in course STD_GOT_F who also passed pre
    regis_std = []
    for student in cour['STD_GOT_F']:
        if len(student) != 0:
            std_id = student['STD_ID']
            regis_std.append(std_id)
    for student in cour['STD_PASSED']:
        if len(student) != 0:
            std_id = student['STD_ID']
            regis_std.append(std_id)
    result = {v: k for v, k in passed_students.items() if v not in regis_std}

    value_counts = {}
    
    for value in result.values():
        value_counts[value] = value_counts.get(value, 0) + 1
    return value_counts

def distribution_course():
    results = []
    for course in distribution_data:
        results.append({'CID': course['CID'], 'CNAME': course['CNAME']})
    return results