import sys
import os
from unittest import result
from pyswip import Prolog
import time
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

from eduplan.rule.assert_rule import *
from eduplan.rule.assert_data import student_data, recieved_grade

def remove_all_data(prolog):
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


def load_mock_data(prolog):

    prolog.assertz("student('64105465555', 'Joe', 'Dep', 'B', 'E', 'B', 'E17', 10706, 3963, 2564, 27101, 2)")

    prolog.assertz("directPrerequisiteOf('A', 'B')")
    prolog.assertz("directPrerequisiteOf('B', 'C')")
    prolog.assertz("directPrerequisiteOf('Z', 'Y')")
    prolog.assertz("directPrerequisiteOf('Y', 'X')")
    prolog.assertz("corequisiteOf('M', 'X')")
    prolog.assertz("corequisiteOf('X', 'M')")

    prolog.assertz("course('A', 'AA', '2', 'l', 1, 1)" )
    prolog.assertz("course('B', 'AB', '2', 'l', 1, 2)" )
    prolog.assertz("course('B2', 'AB2', '2', 'l', 1, 2)")
    prolog.assertz("course('C', 'AC', '3', 'l', 2, 1)" )
    prolog.assertz("course('D', 'AD', '3', 'l', 2, 2)" )
    prolog.assertz("course('E', 'AE', '4', 'l', 3, 1)" )
    prolog.assertz("course('F', 'AI', '4', 'l', 3, 2)" )
    prolog.assertz("course('G', 'AG', '5', 'l', 4, 1)" )
    prolog.assertz("course('H', 'AF', '5', 'l', 4, 2)" )
    prolog.assertz("course('Z', 'AA', '2', 'l', 1, 1)")
    prolog.assertz("course('Y', 'AB2', '2', 'l', 1, 2)")
    prolog.assertz("course('X', 'AB3', '2', 'l', 1, 2)")
    prolog.assertz("course('M', 'AB4', '2', 'l', 1, 2)")

    prolog.assertz("recivedGrade('64105465555', 'A', 'AA', 'A', 65, 1)")
    prolog.assertz("recivedGrade('64105465555', 'B', 'AB', 'F', 65, 2)")
    prolog.assertz("recivedGrade('64105465555', 'B2', 'AB2', 'W', 65, 2)")
    prolog.assertz("recivedGrade('64105465555', 'Z', 'ZZ', 'A', 65, 1)")
    prolog.assertz("receivedGrade('64105465555', 'Y', 'AB2', 'A', 65, 2)") 

    prolog.assertz("recivedGrade('64105465555', 'C', 'AC', 'F', 66, 1)")
    prolog.assertz("recivedGrade('64105465555', 'D', 'AD', '-', 66, 2)")
    prolog.assertz("recivedGrade('64105465555', 'E', 'AE', 'Undefined', 67, 1)")
    prolog.assertz("recivedGrade('64105465555', 'F', 'AI', 'Undefined', 67, 2)")
    prolog.assertz("recivedGrade('64105465555', 'G', 'AG', 'Undefined', 68, 1)")
    prolog.assertz("recivedGrade('64105465555', 'H', 'AF', 'Undefined', 68, 2)")


prolog = Prolog()

class TestPrologRules(unittest.TestCase):
    def setUp(self):
        self.stdID = '64105465555'
        self.futureyear = 2566
    
    def tearDown(self):
        remove_all_data(prolog)

    def test_student_data(self):
        load_mock_data(prolog)
        results = student_data(self.stdID)
        expected = [{'StdFirstName': 'Joe', 'StdLastName': 'Dep', 'CID': 'B', 'FID': 'E', 'DID': 'B', 'MID': 'E17', 'CurID': 10706, 'PlanID': 3963, 'StdRegisterYear': 2564, 'Status': 27101, 'StdSem': 2}]
        self.assertEqual(results, expected)

    def test_pre_course(self):
        load_mock_data(prolog)
        pre_rule()
        expected = [{'PREID': 'A', 'CID': 'C'}, {'PREID': 'Z', 'CID': 'X'}, {'PREID': 'A', 'CID': 'B'}, {'PREID': 'B', 'CID': 'C'}, {'PREID': 'Z', 'CID': 'Y'}, {'PREID': 'Y', 'CID': 'X'}]
        results = pre_Course()
        self.assertEqual(results, expected)

    def test_recieved_grade(self):
        load_mock_data(prolog)
        results = recieved_grade(self.stdID)
        expected = [{'CID': 'A', 'CName': 'AA', 'GRADE': 'A', 'YEAR': 65, 'SEM': 1}, {'CID': 'B', 'CName': 'AB', 'GRADE': 'F', 'YEAR': 65, 'SEM': 2}, {'CID': 'B2', 'CName': 'AB2', 'GRADE': 'W', 'YEAR': 65, 'SEM': 2}, {'CID': 'Z', 'CName': 'ZZ', 'GRADE': 'A', 'YEAR': 65, 'SEM': 1}, {'CID': 'C', 'CName': 'AC', 'GRADE': 'F', 'YEAR': 66, 'SEM': 1}, {'CID': 'D', 'CName': 'AD', 'GRADE': '-', 'YEAR': 66, 'SEM': 2}, {'CID': 'E', 'CName': 'AE', 'GRADE': 'Undefined', 'YEAR': 67, 'SEM': 1}, {'CID': 'F', 'CName': 'AI', 'GRADE': 'Undefined', 'YEAR': 67, 'SEM': 2}, {'CID': 'G', 'CName': 'AG', 'GRADE': 'Undefined', 'YEAR': 68, 'SEM': 1}, {'CID': 'H', 'CName': 'AF', 'GRADE': 'Undefined', 'YEAR': 68, 'SEM': 2}]
        self.assertEqual(results, expected)

    def test_passed_course(self):
        load_mock_data(prolog)
        passed_course_rule()
        results = passed_courses(self.stdID)
        expected = [{'CID': 'A', 'CNAME': 'AA', 'YEAR': 65, 'SEM': 1}, {'CID': 'Z', 'CNAME': 'ZZ', 'YEAR': 65, 'SEM': 1}]
        self.assertEqual(results, expected)

    def test_can_register_1(self):
        load_mock_data(prolog)
        can_register_sub_without_preco_rule()
        expected = [{'CID': 'A', 'SEM': 1}, {'CID': 'B', 'SEM': 2}, {'CID': 'B2', 'SEM': 2}, {'CID': 'C', 'SEM': 1}, {'CID': 'D', 'SEM': 2}, {'CID': 'Z', 'SEM': 1}, {'CID': 'Y', 'SEM': 2}, {'CID': 'X', 'SEM': 2}, {'CID': 'M', 'SEM': 2}]
        results = register_subject(self.stdID, self.futureyear)
        self.assertEqual(results, expected)

    def test_can_register_2(self):
        load_mock_data(prolog)
        pre_rule()
        passed_course_rule()
        can_register_direct_pre_course_rule()
        results = register_subject(self.stdID, self.futureyear)
        expected = [{'CID': 'B', 'SEM': 2}, {'CID': 'Y', 'SEM': 2}]
        self.assertEqual(results, expected)

    def test_can_register_3(self):
        load_mock_data(prolog)
        pre_rule()
        passed_course_rule()
        can_register_pre_course_rule()
        results = register_subject(self.stdID, self.futureyear)
        expected = [{'CID': 'C', 'SEM': 1}, {'CID': 'X', 'SEM': 2}]
        self.assertEqual(results, expected)

    def test_can_register_4(self):
        load_mock_data(prolog)
        can_register_co_course_rule()
        results = register_subject(self.stdID, self.futureyear)
        expected = [{'CID': 'X', 'SEM': 2}, {'CID': 'M', 'SEM': 2}]
        self.assertEqual(results, expected)

    def test_future_course_undefined(self):
        load_mock_data(prolog)
        pre_rule()
        current_year_rule()
        passed_course_rule()
        can_register_sub_without_preco_rule()
        can_register_direct_pre_course_rule()
        can_register_pre_course_rule()
        can_register_co_course_rule()
        future_course_undefined_rule()
        results = future_course(self.stdID)
        expected = [{'CID': 'E', 'CNAME': 'AE', 'YEAR': 2567, 'REGISTERSEM': 1}, {'CID': 'F', 'CNAME': 'AI', 'YEAR': 2567, 'REGISTERSEM': 2}, {'CID': 'G', 'CNAME': 'AG', 'YEAR': 2568, 'REGISTERSEM': 1}, {'CID': 'H', 'CNAME': 'AF', 'YEAR': 2568, 'REGISTERSEM': 2}]
        self.assertEqual(results, expected)

    def test_future_course_fail(self):
        load_mock_data(prolog)
        pre_rule()
        current_year_rule()
        passed_course_rule()
        can_register_sub_without_preco_rule()
        can_register_direct_pre_course_rule()
        can_register_pre_course_rule()
        can_register_co_course_rule()
        future_course_fail_rule()  
        results = future_fail_course(self.stdID)
        expected = [{'CID': 'B', 'CNAME': 'AB', 'YEAR': 2566, 'REGISTERSEM': 2}, {'CID': 'C', 'CNAME': 'AC', 'YEAR': 2567, 'REGISTERSEM': 1}]
        self.assertEqual(results, expected)

    def test_future_course_drop(self):
        load_mock_data(prolog)
        pre_rule()
        current_year_rule()
        passed_course_rule()
        can_register_sub_without_preco_rule()
        can_register_direct_pre_course_rule()
        can_register_pre_course_rule()
        can_register_co_course_rule()
        future_course_drop_rule()  
        results = future_course(self.stdID)
        expected = [{'CID': 'B2', 'CNAME': 'AB2', 'YEAR': 2566, 'REGISTERSEM': 2}]
        self.assertEqual(results, expected)

if __name__ == '__main__':
    unittest.main()