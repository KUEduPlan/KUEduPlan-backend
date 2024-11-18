course("01219114", "Prog 1", 1, 1, 1, [1], [], ["01219115"]).
course("01219115", "Prog 1 Lab", 1, 1, 1, [1], [], ["01219114"]).
course("01219118", "Discrete", 1, 1, 1, [1], [], []).
course("01417167", "Math 1", 1, 1, 1, [1, 2, 3], [], []).
course("01420111", "Physics 1", 1, 1, 1, [1, 2, 3], [], []).
course("01219116", "Prog 2", 1, 2, 1, [2], ["01219114", "01219115"], ["01219117"]).
course("01219117", "Prog 2 Lab", 1, 2, 1, [2], ["01219114", "01219115"], ["01219116"]).
course("01219217", "Algo 1", 1, 2, 1, [2], ["01219118"], []).
course("01204216", "Prob Stat", 1, 2, 1, [2], ["01417167"], []).
course("01417168", "Math 2", 1, 2, 1, [1, 2, 3], ["01417167"], []).
course("01420113", "Physics 1 Lab", 1, 2, 1, [2], [], ["01420111"]).
course("01219212", "Algo Lab", 2, 1, 1, [1], ["01219114", "01219115"], ["01219217"]).
course("01219218", "Algo 2", 2, 1, 1, [1], ["01219217"], []).
course("01219224", "Network", 2, 1, 1, [1], [], []).
course("01219231", "Database", 2, 1, 1, ["01219217"], [], []).
course("01219241", "ISP", 2, 1, 1, ["01219116", "01219117"], [], []).
course("01204461", "AI", 2, 2, 2, [], [], []).
course("01219222", "ComSys", 2, 2, 2, ["01219114", "01219115"], ["01219223"], []).
course("01219223", "ComSys Lab", 2, 2, 2, [], ["01219222"], []).
course("01219243", "Soft Design", 2, 2, 2, ["01219116", "01219117"], [], []).
course("01219335", "DAQ", 2, 2, 2, ["01219114", "01219115"], [], []).
course("01219343", "Testing", 2, 2, 2, ["01219241"], [], []).
course("01219313", "Comm Skill", 3, 1, 1, [], [], []).
course("01219325", "Soft Security", 3, 1, 1, ["01219241"], [], []).
course("01219346", "Soft Process", 3, 1, 1, ["01219241"], [], []).
course("01219366", "KE", 3, 1, 1, ["01219118"], [], []).
course("01219367", "Data Analytics", 3, 1, 1, ["01204216"], [], []).
course("01219395", "Project Prep", 3, 2, 2, ["01219241"], [], []).
course("01219449", "Soft Arch", 3, 2, 2, ["01219241"], [], []).
course("01219461", "Big Data", 3, 2, 2, ["01219217"], [], []).
course("01219462", "Soft AI", 3, 2, 2, ["01219241"], [], []).
course("01219490", "Coop", 4, 1, 1, ["01219241", "01219243"], [], []).
course("01219497", "Seminar", 4, 2, 2, [], [], []).
course("01219499", "Project", 4, 2, 2, ["01219395"], [], []).

ascii_list_to_string(Input, String) :-
    (is_list(Input) -> atom_codes(String, Input) ; String = Input).

convert_integers_to_strings([], []).
convert_integers_to_strings([Elem | Rest], [String | ConvertedRest]) :-
    (integer(Elem) -> number_codes(Elem, Codes), atom_codes(String, Codes) ; String = Elem),
    convert_integers_to_strings(Rest, ConvertedRest).

convert_list_to_strings([], []).
convert_list_to_strings([Elem | Rest], [String | ConvertedRest]) :-
    ascii_list_to_string(Elem, String),
    convert_list_to_strings(Rest, ConvertedRest).

find_courses_by_year_semester(Year, Semester, CourseIDs) :-
    findall((ID, ShortName, Year, Semester, SemOpen, Pre, Co, PreCo), 
            course(ID, ShortName, Year, Semester, SemOpen, Pre, Co, PreCo), 
            CourseIDs).

passed_courses(CurrentYear, CurrentSemester, PassedCourses) :-
    findall((ID, ShortName, Year, Semester, SemOpen, Pre, Co, PreCo),
            (course(ID, ShortName, Year, Semester, SemOpen, Pre, Co, PreCo),
             number(CurrentYear), number(CurrentSemester),
             (Year < CurrentYear ; (Year = CurrentYear, Semester < CurrentSemester))),
            PassedCourses).

future_courses_to_register(CurrentYear, CurrentSemester, FutureCourses) :-
    findall((ID, ShortName, Year, Semester, SemOpen, Pre, Co, PreCo),
            (course(ID, ShortName, Year, Semester, SemOpen, Pre, Co, PreCo),
             number(CurrentYear), number(CurrentSemester),
             (Year > CurrentYear ; (Year = CurrentYear, Semester > CurrentSemester))),
            FutureCourses).

convert_course_data([], []).
convert_course_data([(ID, ShortName, Year, Semester, SemOpen, Pre, Co, PreCo) | Rest], 
                    [(IDString, ShortNameString, Year, Semester, SemOpen, PreStrings, CoStrings, PreCoStrings) | ConvertedRest]) :-
    ascii_list_to_string(ID, IDString),
    ascii_list_to_string(ShortName, ShortNameString),
    convert_integers_to_strings(Pre, PreStrings),
    convert_integers_to_strings(Co, CoStrings),
    convert_integers_to_strings(PreCo, PreCoStrings),
    convert_course_data(Rest, ConvertedRest).

main :-
    CurrentYear = 2,
    CurrentSemester = 1,
    setof((ID, ShortName, CurrentYear, CurrentSemester, SemOpen, Pre, Co, PreCo),
          course(ID, ShortName, CurrentYear, CurrentSemester, SemOpen, Pre, Co, PreCo),
          CurrentCourses),
    convert_course_data(CurrentCourses, ConvertedCurrentCourses),
    write("Courses in Year 2, Semester 1"), nl,
    write(ConvertedCurrentCourses), nl, nl,
    passed_courses(CurrentYear, CurrentSemester, PassedCourses),
    convert_course_data(PassedCourses, ConvertedPassedCourses),
    write("Courses passed by Year 2, Semester 1:"), nl,
    write(ConvertedPassedCourses), nl, nl,
    future_courses_to_register(CurrentYear, CurrentSemester, FutureCourses),
    convert_course_data(FutureCourses, ConvertedFutureCourses),
    write("Courses to register for Year 2, Semester 1:"), nl,
    write(ConvertedFutureCourses), nl.

:- initialization(main).