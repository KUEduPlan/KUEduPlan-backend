from rule.assert_rule import *

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
    assert_student_recived_grade_current_sem_open_plan(student_code)

def remove_all_data():
    prolog.retractall('student(_, _, _, _, _, _, _, _, _, _, _, _)')
    prolog.retractall('register(_, _, _, _, _)')
    prolog.retractall('recivedGrade(_, _, _, _, _, _)')
    prolog.retractall('course(_, _, _, _, _, _)')
    prolog.retractall('directPrerequisiteOf(_, _)')
    prolog.retractall('corequisiteOf(_, _)')
    prolog.retractall('currentYear(_)')

    # Clear Rules
    prolog.retractall('passedCourse(_, _, _, _, _)')
    prolog.retractall('canRegister(_, _, _, _)')
    prolog.retractall('futureCourse(_, _, _, _, _)')
    prolog.retractall('prerequisiteOf(_, _)')
