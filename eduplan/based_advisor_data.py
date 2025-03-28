from pyswip import Prolog
from based_prolog_data import *

prolog = Prolog()
def query_advisee_data(advisor_code):
    results = []
    db = connect_mongo("Advisor")
    collection = db["Advisee"]
    data = collection.find_one({"advisor_code": advisor_code}, {'_id': 0})
    for advisee in data['advisee_list']:
        try:
            open_plan_assert_data(advisee['std_id'])
            student_data = list(prolog.query(f"student('{advisee['std_id']}', StdFirstName, StdLastName, CID, FID, DID, MID, CurID, PlanID, StdRegisterYear, Status, StdSem)"))
            student_data[0]['StdID'] = advisee['std_id']
            results.append(student_data[0])
        except:
            print(f"This student {advisee['std_id']} is not advisee of this advisor")
    return results