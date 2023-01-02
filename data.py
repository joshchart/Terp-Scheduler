import umd_io
from umd_io.apis.tags import courses_api
from umd_io.model.error import Error
from umd_io.model.section import Section
from typing import List
from typing import Optional
import json

import planet_terp
from planet_terp.apis.tags import professors_api
from planet_terp.model.professor import Professor
from planet_terp.apis.tags import grades_api
from planet_terp.model.grades import Grades
from planet_terp import schemas
from pprint import pprint

import csv, os, argparse

io_client = umd_io.ApiClient()
api_client = planet_terp.ApiClient()


def get_sections_for_course(course_id: str, semester_id: str):
    api_instance = courses_api.CoursesApi(io_client)
    path_params = {'course_ids': [course_id]}
    query_params = {'semester': semester_id}
    try:
        api_response = api_instance.get_sections_for_course(
            path_params=path_params,
            query_params=query_params,
        )
        return api_response
    except umd_io.ApiException as e:
        print("Exception when calling CoursesApi->get_sections_for_course: %s\n" % e)


def get_instructors_for_course(course_id: str, semester_id: str):
    result = get_sections_for_course(course_id, semester_id)
    instructor_set = set()
    for i in range(len(result.body)):
        instructors = result.body[i]["instructors"]
        if len(instructors) > 1 and instructors[0] not in instructor_set: #need to only have original so 
            # Hardcode second instructor (CMSC132 202301 had two professors, second one was real)
            instructor_set.add(instructors[1])
        elif len(instructors) == 1:
            instructor_set.add(instructors[0])
    return instructor_set


def _is_professor_not_found(api_exception: planet_terp.ApiException) -> bool:
    if api_exception.status != 400:
        return False
    error_body = api_exception.body.decode("utf-8")
    error = json.loads(error_body)
    return error.get("error") == "professor not found"


def get_rating(professor_name: str) -> Optional[float]: #error when teacher has no ratings
    api_instance = professors_api.ProfessorsApi(api_client)
    query_params = {'name': professor_name}
    try:
        api_response = api_instance.get_a_professor(
            query_params=query_params,
        )
        rating = api_response.body["average_rating"]
        if isinstance(rating, schemas.NoneClass):
            return None
        rating = float(rating)
        return round(rating,2)
    except planet_terp.ApiException as e:
        if _is_professor_not_found(e):
            return None
        print("Exception when calling ProfessorsApi->get_a_professor: %s\n" % e)


def _get_grades_for_course(course_id: str, professor: str):
    api_instance = grades_api.GradesApi(api_client)
    query_params = {
        'course': course_id,
        'professor': professor,
    }
    try:
        return api_instance.get_grades(query_params=query_params)
    except planet_terp.ApiException as e:
        if _is_professor_not_found(e):
            return None
        print("Exception when calling GradesApi->get_grades: %s\n" % e)


def _calculate_gpa(api_response):
    grade_points = {"A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3, 
                    "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0, "W": 0.0}
    grade_counts = {grade: 0 for grade in grade_points}
    for section in api_response.body:
        for grade in grade_counts:
            grade_counts[grade] += int(section[grade])

    gpa_accumulator = 0.0
    total_count = 0
    for grade_name, count in grade_counts.items():
        gpa_accumulator += (grade_points[grade_name] * count)
        total_count += count
    return round(gpa_accumulator / total_count,2)


def get_gpa_for_course(course_id: str, professor: str) -> Optional[float]:
    try:
        api_response = _get_grades_for_course(course_id, professor)
        if api_response is None:
            return None
        return _calculate_gpa(api_response)
    except ZeroDivisionError as e:
        # print("Error no data for that class")
        pass


def main():
    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--courses', required=True, help='comma-separated list of courses')
    parser.add_argument('--semester', required=True, help='semester code')
    parser.add_argument('--output', required=True, help='output file name')
    args = parser.parse_args()

    courses = args.courses.split(',')
    # courses = args.courses
    semester = args.semester
    output_file = args.output

    # Open a file for writing
    with open(output_file, 'w', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile, delimiter=',')

        # Write the header row
        writer.writerow(['Course', 'Teacher', 'GPA', 'Rating'])

        # Gets data 
        for n in range(len(courses)):
            cur_prof = get_instructors_for_course(courses[n], semester)
            data = {name: (get_gpa_for_course(courses[n],name),get_rating(name)) for name in cur_prof}

            # Write some data rows
            for key, value in data.items():
                writer.writerow([courses[n], key, value[0], value[1]])

    csv_path = os.getcwd() + '/' + output_file
    print(csv_path)
    

if __name__ == "__main__":
    main()
    # pass



#TESTING
# course = input("Enter your course: ")
# semester = input("Enter your semester: ")

#cur_prof = get_instructors_for_course("MATH240", "202301")
# data = {name: (get_gpa_for_course("MATH240",name),get_rating(name)) for name in cur_prof}

# for key, value in data.items():
#     print(f"Teacher: {key} GPA: {value[0]} Rating: {value[1]}")

#print({name: get_rating(name) for name in cur_prof})
# print({name: get_gpa_for_course("MATH240",name) for name in cur_prof}) 

# print(get_instructors_for_course("MATH240", "202301"))



