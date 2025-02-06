import sys
import os
from pyswip import Prolog
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)


import unittest
from pyswip import Prolog
from eduplan.rule.rule import assert_rules, pre_Course, passed_courses, register_subject, future_course

def load_mock_data(prolog):
    prolog.assertz("student('S1', 'John Doe', 'CSE', '2022', 'A', 'B', 'C', 'D', 'E', 2022, 'F', 'G')")
    prolog.assertz("course('C1', 'Intro to CS', 'CSE101', 3, 1, 1)")
    prolog.assertz("course('C2', 'Data Structures', 'CSE102', 3, 2, 2)")
    prolog.assertz("directPrerequisiteOf('C1', 'C2')")
    prolog.assertz("recivedGrade('S1', 'C1', 'A', 'B', 2022, 1)")
    prolog.assertz("register('S1', 'C1', 'A', 2022, 1)")
    prolog.assertz("corequisiteOf('C3', 'C2')")
    prolog.assertz("recivedGrade('S1', 'C3', 'A', 'Undefined', 2022, 2)")
    prolog.assertz("recivedGrade('S1', 'C2', 'A', 'F', 2023, 1)")

class TestPrologRules(unittest.TestCase):
    
    def setUp(self):
        self.prolog = Prolog()
        assert_rules()
        load_mock_data(self.prolog)
    
    def test_pre_Course(self):
        result = pre_Course()
        expected = [{'PREID': 'C1', 'CID': 'C2'}]
        self.assertEqual(result, expected)
    
    def test_passed_courses(self):
        result = passed_courses('S1')
        expected = [{'CID': 'C1', 'YEAR': 2022, 'SEM': 1}]
        self.assertEqual(result, expected)
    
    # def test_register_subject(self):
    #     result = register_subject('S1', 2023)
    #     expected = [{'CID': 'C2', 'SEM': 2}]
    #     self.assertIn({'CID': 'C2', 'SEM': 2}, result)
    
    # def test_future_course(self):
    #     result = future_course('S1')
    #     expected = [{'CID': 'C2', 'YEAR': 2024, 'REGISTERSEM': 2}]
    #     self.assertIn({'CID': 'C2', 'YEAR': 2024, 'REGISTERSEM': 2}, result)
    
if __name__ == '__main__':
    unittest.main()