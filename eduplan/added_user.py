from passlib.context import CryptContext
from database.connect_database import connect_client
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = []


client = connect_client()
db = client["Authen"]
collection = db["UserData"]

# Insert users into the database
collection.insert_many(fake_users_db)

print("Users inserted successfully into MongoDB.")

mock_advisor_data = []

mock_advisee_data = []

db_advisor = client["Advisor"]
collection_advisor = db_advisor["AdvisorData"]
collection_advisee = db_advisor["Advisee"]

collection_advisor.insert_many(mock_advisor_data)
collection_advisee.insert_many(mock_advisee_data)

mock_curr_data = []

db_curr = client["CurriculumnAdmin"]
collection_curr= db_curr["AdminData"]
collection_curr.insert_many(mock_curr_data)