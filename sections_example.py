import planet_terp
from planet_terp.apis.tags import grades_api
from planet_terp.model.grades import Grades
from pprint import pprint
# Defining the host is optional and defaults to https://planetterp.com/api/v1
# See configuration.py for a list of all supported configuration parameters.


api_client = planet_terp.ApiClient()


def _get_grades_for_course(course_id: str, professor: str):
    api_instance = grades_api.GradesApi(api_client)
    query_params = {
        'course': course_id,
        'professor': professor,
    }
    try:
        return api_instance.get_grades(query_params=query_params)
    except planet_terp.ApiException as e:
        print("Exception when calling GradesApi->get_grades: %s\n" % e)


def _calculate_gpa(api_response):
    grade_points = {"A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0, "W": 0.0}
    grade_counts = {grade: 0 for grade in grade_points}
    for section in api_response.body:
        for grade in grade_counts:
            grade_counts[grade] += int(section[grade])

    gpa_accumulator = 0.0
    total_count = 0
    for grade_name, count in grade_counts.items():
        gpa_accumulator += (grade_points[grade_name] * count)
        total_count += count
    return gpa_accumulator / total_count


def get_gpa_for_course(course_id: str, professor: str) -> float:
    try:
        api_response = _get_grades_for_course(course_id, professor)
        return _calculate_gpa(api_response)
    except ZeroDivisionError as e:
        print("Error no data for that class")

