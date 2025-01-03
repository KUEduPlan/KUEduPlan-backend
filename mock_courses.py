from unittest import result
from pyswip import Prolog
from fastapi import FastAPI
import time

app = FastAPI()

# Initialize Prolog
prolog = Prolog()

# Define course data
def assert_courses():
    # Assert Department data
    prolog.asserta('department("1", "Engineering")')
    prolog.assertz('major("1", "Software Engineering")')
    prolog.assertz('departmentOf("1", "1")')

    # Assert RequiredCourseByMajor data
    prolog.assertz('requiredCourseByMajor("1", "101")')
    prolog.assertz('requiredCourseByMajor("1", "102")')
    prolog.assertz('requiredCourseByMajor("1", "103")')
    prolog.assertz('requiredCourseByMajor("1", "104")')
    prolog.assertz('requiredCourseByMajor("1", "105")')
    prolog.assertz('requiredCourseByMajor("1", "106")')

    # Assert Course data
    prolog.assertz('course("101", "Introduction to CS", 1, "1")')
    prolog.assertz('course("102", "Algorithms", 2, "2")')
    prolog.assertz('course("103", "Data Analysis", 1, "1")')
    prolog.assertz('course("104", "Machine Learning", 3, "2")')
    prolog.assertz('course("105", "Robotics Engineering", 2, "1")')
    prolog.assertz('course("106", "AI for Robotics", 4, "2")')

    # Assert Prerequisite data
    prolog.assertz('directPrerequisiteOf("101", "102")')
    prolog.assertz('corequisiteOf("101", "102")')

    prolog.assertz('directPrerequisiteOf("102", "105")')
    prolog.assertz('corequisiteOf("102", "105")')
    prolog.assertz('''prerequisiteOf(A, C) :-
                   directPrerequisiteOf(A, B), 
                   directPrerequisiteOf(B, C),
                   A \= C
                   ''')

    
    # Assert Student data year 2 semester 1
    prolog.assertz('student(1001, "Alice Johnson", 2566, "Bachelor", "1", "1", "1", "Active")')

    # Assert Grades and Registration data
    prolog.assertz('recievedGrade(1001, "105", "Undefinded", 2567)')
    prolog.assertz('recievedGrade(1001, "104", "Undefinded", 2568)')
    prolog.assertz('recievedGrade(1001, "102", "Undefinded", 2567)')
    prolog.assertz('recievedGrade(1001, "106", "Undefinded", 2569)')
    prolog.assertz('recievedGrade(1001, "101", "F", 2566)')
    prolog.assertz('recievedGrade(1001, "103", "B", 2566)')
    prolog.assertz('register(1001, "105", 2567, "1")')
    prolog.assertz('register(1001, "103", 2566, "1")') 
    prolog.assertz('register(1001, "101", 2566, "1")')  # Added missing registration for course 101

    # Asset current year
    prolog.assertz(f'currentYear({time.localtime().tm_year + 543 - 1})')


    # Assert the passedCourse rule with correct course/4 references
    prolog.assertz(
        '''passedCourse(StdId, CId, RegisterYear, RegisterSem) :- 
        student(StdId, _, _, _, _, _, _, _), 
        course(CId, _, _, _),
        recievedGrade(StdId, CId, Grade, RegisterYear), 
        register(StdId, CId, RegisterYear, RegisterSem), 
        Grade \= "Undefinded",
        Grade \= "W"
        '''
    )

    # # # Register major subject without pre, co, pre-co
    prolog.assertz(
        '''canRegister(StdId, CId, FutureYear, Sem) :-
        course(CId, _, AllowYear, OpenSem),
        student(StdId, _, StdYear, _, _, _, _, _),
        FutureYear - StdYear >= AllowYear,
        Sem == OpenSem
        '''
    )

    # Register pre course prerequisiteOf
    prolog.assertz('''
        canRegister(StdId, CId, Year, StdSem) :-
            student(StdId, _, StdYear, _, _, _, StdSem, _),
            course(CId, _, AllowYear, OpenSem),
            prerequisiteOf(PreId, CId),
            PreId \= CId,                          
            StdSem == OpenSem,                 
            Year - StdYear >= AllowYear,       
            passedCourse(StdId, PreId, RegisterYear, RegisterSem), 
            RegisterYear =< Year,              
            RegisterSem \= StdSem      
    ''')
    # directPrerequisiteOf
    prolog.assertz('''
        canRegister(StdId, CId, Year, StdSem) :-
            student(StdId, _, StdYear, _, _, _, StdSem, _),
            course(CId, _, AllowYear, OpenSem),
            directPrerequisiteOf(PreId, CId),
            PreId \= CId,                          
            StdSem == OpenSem,                 
            Year - StdYear >= AllowYear,       
            passedCourse(StdId, PreId, RegisterYear, RegisterSem), 
            RegisterYear =< Year,              
            RegisterSem \= StdSem      
    ''')

    # # Register Pre-Co
    prolog.assertz('''
    canRegister(StdId, CId, Year, StdSem) :-
        currentYear(Year),
        student(StdId, _, StdYear, _, _, _, StdSem, _),
        course(CId, _, AllowYear, OpenSem),
        corequisiteOf(CID2, CId),               % Course has a corequisite
        register(StdId, CID2, Year, StdSem),    % Corequisite is already registered
        StdSem == OpenSem,                      % Course is open in the current semester
        Year - StdYear >= AllowYear             % Student meets the year requirement
    ''')

    # Future course not register ########
    prolog.assertz(
        '''futureCourse(StdId, CId, FutureYear, OpenSem) :-
            student(StdId, _, StdYear, _, _, _, StdSem, _),
            recievedGrade(StdId, CId, Grade, RegisterYear),
            course(CId, _, AllowYear, OpenSem),
            Grade == "Undefinded",
            currentYear(Year),
            AllowYearDiff is AllowYear - (Year - StdYear),
            FutureYear is Year + AllowYearDiff,
            FutureYear - StdYear >= AllowYear,
            canRegister(StdId, CId, FutureYear, OpenSem)
        '''
    )
        # Future course not register ########
    prolog.assertz(
        '''futureCourse(StdId, CId, FutureYear, OpenSem) :-
            student(StdId, _, StdYear, _, _, _, StdSem, _),
            recievedGrade(StdId, CId, Grade, RegisterYear),
            course(CId, _, AllowYear, OpenSem),
            Grade == "F",
            currentYear(Year),
            AllowYearDiff is AllowYear - (Year - StdYear),
            FutureYear is Year + AllowYearDiff,
            canRegister(StdId, CId, FutureYear, OpenSem)
        '''
    )
    

# Query for passed courses
def register_subject(StdID):
    results = list(prolog.query(f"canRegister({StdID}, CID, YEAR, SEM)"))
    print("Can register")
    print(results)

def course_data():
    results = list(prolog.query("course(CID, CNAME, ALLOWYEAR, OPENSEM)"))
    for i in range(len(results)):
        results[i]['CID'] = results[i]['CID'].decode('utf-8')
        results[i]['CNAME'] = results[i]['CNAME'].decode('utf-8')
        results[i]['OPENSEM'] = results[i]['OPENSEM'].decode('utf-8')
    return results

def required_course():
    results = list(prolog.query("requiredCourseByMajor(MAJOR, COURSE)"))
    return results

def student_data(StdID):
    results = list(prolog.query(f"student({StdID}, NAME, YEAR, PROGRAM, MID, DID, SEM, STATUS)"))
    results[0]['NAME'] = results[0]['NAME'].decode('utf-8')
    results[0]['PROGRAM'] = results[0]['PROGRAM'].decode('utf-8')
    results[0]['STATUS'] = results[0]['STATUS'].decode('utf-8')
    return results

def passed_courses(StdID):
    results = list(prolog.query(f"passedCourse({StdID}, CID, YEAR, REGISTERSEM)"))
    for i in range(len(results)):
        results[i]['REGISTERSEM'] = results[i]['REGISTERSEM'].decode('utf-8')
    return results

def recieved_grade(StdID):
    results = list(prolog.query(f"recievedGrade({StdID}, CID, GRADE, YEAR)"))
    for i in range(len(results)):
        results[i]['GRADE'] = results[i]['GRADE'].decode('utf-8')
    return results

def future_course(StdID):
    results = list(prolog.query(f"futureCourse({StdID}, CID, YEAR, REGISTERSEM)"))
    for i in range(len(results)):
        results[i]['REGISTERSEM'] = results[i]['REGISTERSEM'].decode('utf-8')
    # print(results)
    return results

def pre_Course():
    results_direct_courses = list(prolog.query("directPrerequisiteOf(PREID, CID)"))
    results_pre_courses = list(prolog.query("prerequisiteOf(PREID, CID)"))
    results = results_pre_courses + results_direct_courses
    for i in range(len(results)):
        results[i]['CID'] = results[i]['CID'].decode('utf-8')
        results[i]['PREID'] = results[i]['PREID'].decode('utf-8')
    return results
# Main function
def main():
    assert_courses()
    pre = pre_Course()
    print(pre)

# Run the script
if __name__ == "__main__":
    main()