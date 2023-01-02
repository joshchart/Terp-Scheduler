import umd_io
from umd_io.apis.tags import courses_api
from umd_io.model.error import Error
from umd_io.model.section import Section
from pprint import pprint
from typing import List
# Defining the host is optional and defaults to https://api.umd.io/v1
# See configuration.py for a list of all supported configuration parameters.

api_client = umd_io.ApiClient()

def get_sections_for_course(course_id: str, semester_id: str):
    api_instance = courses_api.CoursesApi(api_client)
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

#OLD Method (REAL)
# def get_instructors_for_course(course_id: str, semester_id: str):
#     result = get_sections_for_course(course_id, semester_id)
#     instructor_set = set()
#     for i in range(len(result.body)):
#         instructors = result.body[i]["instructors"]
#         if len(instructors) > 1:
#             # Hardcode second instructor (CMSC132 202301 had two professors, second one was real)
#             instructor = instructors[1]
#         else:
#             instructor = instructors[0]
#         instructor_set.add(str(instructor))
#     return instructor_set

print(get_instructors_for_course("GEOL110","202301"))
