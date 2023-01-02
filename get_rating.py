import planet_terp
from planet_terp.apis.tags import professors_api
from planet_terp.model.professor import Professor
from pprint import pprint

api_client = planet_terp.ApiClient()

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


def _is_professor_not_found(api_exception: planet_terp.ApiException) -> bool:
    if api_exception.status != 400:
        return False
    error_body = api_exception.body.decode("utf-8")
    error = json.loads(error_body)
    return error.get("error") == "professor not found"

# def get_rating(professor_name: str) -> float:
#     api_instance = professors_api.ProfessorsApi(api_client)
#     query_params = {'name': professor_name}
#     try:
#         api_response = api_instance.get_a_professor(
#             query_params=query_params,
#         )
#         return float(api_response.body["average_rating"])
#     except planet_terp.ApiException as e:
#         print("Exception when calling ProfessorsApi->get_a_professor: %s\n" % e)

professors = ["Abba Gumel"]
print({name: get_rating(name) for name in professors})