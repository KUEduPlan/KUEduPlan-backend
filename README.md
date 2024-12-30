# KUEduPlan-backend


# Get all courses that student need to studdy
input -> student Id
Filter from mongoDB to get the data of student toget major id
prolog input majoerID
```required_course()```

# Student data
input -> student Id
```student_data(StdID)```
```[{'NAME': 'Alice Johnson', 'YEAR': 2023, 'PROGRAM': 'Bachelor', 'MID': 1, 'DID': 1, 'SEM': 1, 'STATUS': 'Active'}]```

# Student Passed course
input -> student Id
``` [{'CNAME': 101, 'REGISTEREYEAR': 2023, 'REGISTERSEM': 1}, {'CNAME': 103, 'REGISTEREYEAR': 2023, 'REGISTERSEM': 1}]```

# Student Recieved grade
input -> student Id
```[{'CID': 101, 'GRADE': 'A', 'YEAR': 2023}, {'CID': 103, 'GRADE': 'B', 'YEAR': 2023}]```

# Future Course

# Can register