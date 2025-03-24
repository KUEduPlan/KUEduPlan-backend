from pyswip import Prolog
from based_prolog_data import *

mock_advisor_data = [{
  "advisor_code": "advisoruser",
  "first_name_th": "Norris",
  "last_name_th": "Lando",
  "campus_code": "B",
  "faculty_code": "E",
  "dept_code": "B",
  "major_code": "E17",
  "campus_name_th": "บางเขน",
  "faculty_name_th": "วิศวกรรมศาสตร์",
  "dept_name_th": "วิศวกรรมคอมพิวเตอร์",
  "major_name_th": "วิศวกรรมซอฟต์แวร์และความรู้",
  "cur_id": 10706,
  "plan_id": 3963,
  "status_code": "17004",
  "status_code_desc": "พิเศษ (นานาชาติ)"
}]

mock_advisee_data = [{
  "advisor_code": "advisoruser",
  "advisee_list": [
	{"std_id": "6410546131"},
    {"std_id": "6410545541"}
]}]

prolog = Prolog()
def query_advisee_data(advisor_code):
    results = []
    for data in mock_advisee_data:
        if data['advisor_code'] == advisor_code:
            for advisee in data['advisee_list']:
                try:
                    open_plan_assert_data(advisee['std_id'])
                    student_data = list(prolog.query(f"student('{advisee['std_id']}', StdFirstName, StdLastName, CID, FID, DID, MID, CurID, PlanID, StdRegisterYear, Status, StdSem)"))
                    student_data[0]['StdID'] = advisee['std_id']
                    results.append(student_data[0])
                except:
                    print(f"This student {advisee['std_id']} is not advisee of this advisor")
    return results