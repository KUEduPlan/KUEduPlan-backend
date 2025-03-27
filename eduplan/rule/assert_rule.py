import sys
import os
from pyswip import Prolog
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from eduplan.rule.assert_data import *
prolog = Prolog()

def current_year_rule():
    prolog.assertz(f'currentYear({time.localtime().tm_year + 544 - 1})')
    print(time.localtime().tm_year + 544 - 1)

def pre_rule():
    prolog.assertz('''prerequisiteOf(A, C) :-
                   directPrerequisiteOf(A, B), 
                   directPrerequisiteOf(B, C),
                   A \= C
                   ''')

def passed_course_rule():
    prolog.assertz(('''passedCourse(StdID, CID, CNAME, YEAR, SEM) :-
    student(StdID, _, _, _, _, _, _, _, _, _, _, _),
    recivedGrade(StdID, CID, CNAME, GRADE, YEAR, SEM),
    GRADE \= 'F',
    GRADE \= 'W',
    GRADE \= 'Undefined',
    GRADE \= '-'
    '''
    ))

def can_register_sub_without_preco_rule():
     # Register major subject without pre, co, pre-co
    prolog.assertz(
        '''canRegister(StdID, CId, FutureYear, OpenSem) :-
        course(CId, _, _, _, AllowYear, OpenSem),
        student(StdID, _, _, _, _, _, _, _, _, StdYear, _, _),
        FutureYear - StdYear >= AllowYear
        '''
    )

def can_register_direct_pre_course_rule():
    # Register direct pre-course prerequisiteOf
    prolog.assertz('''
        canRegister(StdId, CId, Year, OpenSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, _),
            course(CId, _, _, _, AllowYear, OpenSem),
            directPrerequisiteOf(PreId, CId),                                    
            Year - StdYear >= AllowYear,       
            passedCourse(StdId, PreId, PreName, RegisterYear, RegisterSem), 
            RegisterYear =< Year             
    ''')

def can_register_pre_course_rule():
    # Register pre-course prerequisiteOf
    prolog.assertz('''
        canRegister(StdId, CId, Year, OpenSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, _),
            course(CId, _, _, _, AllowYear, OpenSem),
            prerequisiteOf(PreId, CId),                                     
            Year - StdYear >= AllowYear,       
            passedCourse(StdId, PreId, PreName, RegisterYear, RegisterSem), 
            RegisterYear =< Year             
    ''')

def can_register_co_course_rule():
    # Register pre-course prerequisiteOf
    prolog.assertz('''
        canRegister(StdId, CId, Year, OpenSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, _),
            course(CId, _, _, _, AllowYear, OpenSem),
            corequisiteOf(PreId, CId),                                    
            Year - StdYear >= AllowYear           
    ''')

def future_course_undefined_rule(): 
    ## F
    # Future course not register ########
    prolog.assertz(
        '''futureCourse(StdId, CId, CNAME, FutureYear, OpenSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, _),
            recivedGrade(StdId, CId, _, Grade, RegisterYear, _),
            course(CId, CNAME, _, _, AllowYear, OpenSem),
            Grade == 'Undefined',
            currentYear(Year),
            AllowYearDiff is AllowYear - (Year - StdYear),
            FutureYear is Year + AllowYearDiff,
            FutureYear - StdYear >= AllowYear,
            canRegister(StdId, CId, FutureYear, _)
        '''
    )

    ## W
    prolog.assertz(   
        '''futureCourse(StdId, CId, CNAME, FutureYear, OpenSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, _),
            recivedGrade(StdId, CId, _, Grade, RegisterYear, _),
            course(CId, CNAME, _, _, AllowYear, OpenSem),
            Grade == 'Undefined',
            currentYear(Year),
            CheckAllowYear is  Year - StdYear -1,
            CheckAllowYear >= AllowYear,
            RecievedYear is RegisterYear + 2500,
            FutureYear is RecievedYear + 1,
            canRegister(StdId, CId, FutureYear, OpenSem)
        '''
    )

def future_course_fail_rule():
    # Future course not register ########
    # prolog.assertz(
    #     '''futureCourse(StdId, CId, CNAME, FutureYear, OpenSem) :-
    #         student(StdId, _, _, _, _, _, _, _, _, StdYear, _, StdSem),
    #         recivedGrade(StdId, CId, _, Grade, RegisterYear, _),
    #         course(CId, CNAME, _, _, AllowYear, OpenSem),
    #         Grade == 'F',
    #         currentYear(Year),
    #         AllowYearDiff is  AllowYear - (Year - StdYear),
    #         FutureYear is Year + AllowYearDiff + 1,
    #         canRegister(StdId, CId, FutureYear, OpenSem)
    #     '''
    # )

    prolog.assertz(
        '''futureCourse(StdId, CId, CNAME, FutureYear, OpenSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, StdSem),
            recivedGrade(StdId, CId, _, Grade, RegisterYear, _),
            course(CId, CNAME, _, _, AllowYear, OpenSem),
            Grade == 'F',
            currentYear(Year),
            CheckAllowYear is  Year - StdYear -1,
            CheckAllowYear >= AllowYear,
            RecievedYear is RegisterYear + 2500,
            FutureYear is RecievedYear + 1,
            canRegister(StdId, CId, FutureYear, OpenSem)
        '''
    )

def future_course_drop_rule():
    # prolog.assertz(
    #     '''futureCourse(StdId, CId, CNAME, FutureYear, OpenSem) :-
    #         student(StdId, _, _, _, _, _, _, _, _, StdYear, _, StdSem),
    #         recivedGrade(StdId, CId, _, Grade, RegisterYear, _),
    #         course(CId, CNAME, _, _, AllowYear, OpenSem),
    #         Grade == 'W',
    #         currentYear(Year),
    #         AllowYearDiff is AllowYear - (Year - StdYear),
    #         FutureYear is Year + AllowYearDiff + 1,
    #         canRegister(StdId, CId, FutureYear, _)
    #     '''
    # )
    prolog.assertz(
        '''futureCourse(StdId, CId, CNAME, FutureYear, OpenSem) :-
            student(StdId, _, _, _, _, _, _, _, _, StdYear, _, StdSem),
            recivedGrade(StdId, CId, _, Grade, RegisterYear, _),
            course(CId, CNAME, _, _, AllowYear, OpenSem),
            Grade == 'W',
            currentYear(Year),
            CheckAllowYear is  Year - StdYear - 1,
            CheckAllowYear >= AllowYear,
            RecievedYear is RegisterYear + 2500,
            FutureYear is RecievedYear + 1,
            canRegister(StdId, CId, FutureYear, OpenSem)
        '''
    )


def assert_rules():
    current_year_rule()
    pre_rule()
    passed_course_rule()
    can_register_sub_without_preco_rule()
    can_register_pre_course_rule()
    can_register_direct_pre_course_rule()
    can_register_co_course_rule()
    future_course_undefined_rule()
    future_course_fail_rule()
    future_course_drop_rule()
    

def pre_Course():
    results_direct_courses = list(prolog.query("directPrerequisiteOf(PREID, CID)"))
    results_pre_courses = list(prolog.query("prerequisiteOf(PREID, CID)"))
    results = results_pre_courses + results_direct_courses
    return results

def passed_courses(StdID):
    results = list(prolog.query(f"passedCourse('{StdID}', CID, CNAME,YEAR, SEM)"))
    return results

def register_subject(StdID, futureyear):
    results = list(prolog.query(f"canRegister('{StdID}',CID, {futureyear}, SEM)"))
    return results

def future_course(StdID):
    results = list(prolog.query(f"futureCourse('{StdID}', CID, CNAME, YEAR, SEM)"))
    return results

def future_fail_course(StdID):
    results = list(prolog.query(f"futureCourse('{StdID}', CID, CNAME, YEAR, SEM)"))
    df = pd.DataFrame(results)
    df_unique = df.drop_duplicates()
    df_list = df_unique.to_dict(orient="records")
    return df_list