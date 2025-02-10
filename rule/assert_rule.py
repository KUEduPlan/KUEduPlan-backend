import sys
import os
from pyswip import Prolog
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from eduplan.rule.assert_data import *

prolog = Prolog()

def assert_rules():
    prolog.assertz(f'currentYear({time.localtime().tm_year + 544 - 1})')

    # directPrerequisiteOf(PreCID, CID)
    # prerequisiteOf(PreCID, CID)
    prolog.assertz('''prerequisiteOf(A, C) :-
                   directPrerequisiteOf(A, B), 
                   directPrerequisiteOf(B, C),
                   A \= C
                   ''')
    
    # Assert the passedCourse rule with correct course/4 references
    prolog.assertz(('''passedCourse(StdID, CID, CNAME, YEAR, SEM) :-
        student(StdID, _, _, _, _, _, _, _, _, _, _, _),
        recivedGrade(StdID, CID, CNAME, GRADE, YEAR, SEM),
        GRADE \= 'F',
        GRADE \= 'W',
        GRADE \= 'Undefined'
        '''
    ))

    # Register major subject without pre, co, pre-co
    prolog.assertz(
        '''canRegister(StdID, CId, FutureYear, Sem) :-
        course(CId, _, _, _, AllowYear, OpenSem),
        student(StdID, _, _, _, _, _, _, _, _, StdYear, _, _),
        FutureYear - StdYear >= AllowYear,
        Sem == OpenSem
        '''
    )

    # Register pre course prerequisiteOf
    prolog.assertz('''
        canRegister(StdId, CId, Year, StdSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, StdSem),
            course(CId, _, _, _, AllowYear, OpenSem),
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
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, StdSem),
            course(CId, _, _, _, AllowYear, OpenSem),
            directPrerequisiteOf(PreId, CId),
            PreId \= CId,                          
            StdSem == OpenSem,                 
            Year - StdYear >= AllowYear,       
            passedCourse(StdId, PreId, RegisterYear, RegisterSem), 
            RegisterYear =< Year,              
            RegisterSem \= StdSem      
    ''')

    # Register Pre-Co
    prolog.assertz('''
    canRegister(StdId, CId, Year, StdSem) :-
        currentYear(Year),
        student(StdId, _, _, _, _, _, _, _, _, StdYear, _, StdSem),
        course(CId, _, _, _, AllowYear, OpenSem),
        corequisiteOf(CID2, CId),               % Course has a corequisite
        register(StdId, CID2, _, Year, StdSem), % Corequisite is already registered
        StdSem == OpenSem,                      % Course is open in the current semester
        Year - StdYear >= AllowYear             % Student meets the year requirement
    ''')

    # Future course not register ########
    prolog.assertz(
        '''futureCourse(StdId, CId, CNAME, FutureYear, OpenSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, StdSem),
            recivedGrade(StdId, CId, _, Grade, RegisterYear, _),
            course(CId, CNAME, _, _, AllowYear, OpenSem),
            Grade == "Undefined",
            currentYear(Year),
            AllowYearDiff is AllowYear - (Year - StdYear),
            FutureYear is Year + AllowYearDiff,
            FutureYear - StdYear >= AllowYear,
            canRegister(StdId, CId, FutureYear, OpenSem)
        '''
    )

    # Future course not register ########
    prolog.assertz(
        '''futureCourse(StdId, CId, CNAME, FutureYear, OpenSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, StdSem),
            recivedGrade(StdId, CId, _, Grade, RegisterYear, _),
            course(CId, CNAME, _, _, AllowYear, OpenSem),
            Grade == "F",
            currentYear(Year),
            AllowYearDiff is AllowYear - (Year - StdYear),
            FutureYear is Year + AllowYearDiff,
            canRegister(StdId, CId, FutureYear, OpenSem)
        '''
    )

    prolog.assertz(
        '''futureCourse(StdId, CId, CNAME, FutureYear, OpenSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, StdSem),
            recivedGrade(StdId, CId, _, Grade, RegisterYear, _),
            course(CId, CNAME, _, _, AllowYear, OpenSem),
            Grade == "W",
            currentYear(Year),
            AllowYearDiff is AllowYear - (Year - StdYear),
            FutureYear is Year + AllowYearDiff,
            canRegister(StdId, CId, FutureYear, OpenSem)
        '''
    )
def pre_Course():
    results_direct_courses = list(prolog.query("directPrerequisiteOf(PREID, CID)"))
    results_pre_courses = list(prolog.query("prerequisiteOf(PREID, CID)"))
    results = results_pre_courses + results_direct_courses
    return results

def passed_courses(StdID):
    results = list(prolog.query(f"passedCourse({StdID}, CID, CNAME,YEAR, SEM)"))
    return results

def register_subject(StdID, futureyear):
    results = list(prolog.query(f"canRegister({StdID},CID, {futureyear}, SEM)"))
    return results

def future_course(StdID):
    results = list(prolog.query(f"futureCourse({StdID}, CID, CNAME, YEAR, REGISTERSEM)"))
    return results